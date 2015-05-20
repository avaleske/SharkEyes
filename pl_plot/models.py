from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files import File
import math
import os
from django.conf import settings
from celery import group
from datetime import datetime, time, tzinfo, timedelta
from django.utils import timezone
from celery import shared_task
from pl_plot import plot_functions
from pl_plot.plotter import Plotter, WaveWatchPlotter
from pl_download.models import DataFile, DataFileManager,WaveWatchDataFile
from django.db.models.aggregates import Max
from uuid import uuid4
from scipy.io import netcdf_file
import numpy
import shutil

HOW_LONG_TO_KEEP_FILES = 10


class OverlayManager(models.Manager):
    @staticmethod
    def get_all_base_definition_ids():
        return OverlayDefinition.objects.values_list('id', flat=True).filter(is_base=True)

    # Team 1 says: todo this will fail for multiple zoom levels
    @staticmethod
    def get_newest_untiled_overlay_ids():
        # assuming newer overlays have higher primary keys. Seems reasonable.
        overlay_definitions = OverlayDefinition.objects.annotate(newest_overlay_id=Max('overlay__id'))
        newest_overlays = Overlay.objects.filter(id__in=[od.newest_overlay_id for od in overlay_definitions])
        return newest_overlays.filter(is_tiled=False).values_list('id', flat=True)

    @classmethod
    def get_next_few_days_of_untiled_overlay_ids(cls):
        # starts with "present" overlay, which is the closest to now, forward or backwards, and goes forward 4 days or
        # however far we have data, whichever is less
        # here assuming that the primary keys for the overlays are only monotonically increasing
        # and that the newer one is better.
        next_few_days_of_overlays = Overlay.objects.filter(
            applies_at_datetime__gte=timezone.now()-timedelta(hours=2),
            applies_at_datetime__lte=timezone.now()+timedelta(days=4)
        )
        and_the_newest_for_each = next_few_days_of_overlays.values('definition', 'applies_at_datetime', 'zoom_levels')\
            .annotate(newest_id=Max('id'))
        that_are_not_tiled = and_the_newest_for_each.filter(is_tiled=False)
        ids_of_these = that_are_not_tiled.values_list('newest_id', flat=True)
        return ids_of_these

    @classmethod
    def get_next_few_days_of_tiled_overlays(cls):

        # Pick how many days into the future and past we want to display overlays for
        next_few_days_of_wave_overlays = Overlay.objects.filter(
            applies_at_datetime__gte=timezone.now()-timedelta(hours=2),
            applies_at_datetime__lte=timezone.now()+timedelta(days=4),
            definition_id=4,
            is_tiled=True,
            definition__is_base=True
        )

        next_few_days_of_sst_overlays = Overlay.objects.filter(
            applies_at_datetime__gte=timezone.now()-timedelta(hours=2),
            applies_at_datetime__lte=timezone.now()+timedelta(days=4),
            definition_id__in=[3 , 1],
            is_tiled=True,
            definition__is_base=True
        )

        # Get the newest overlay for each Model type and time. This assumes that for a certain model date,
        # a larger ID value
        # indicates a more recent overlay. Note that a higher ID does NOT by itself indicate a more RECENT model date
        # because a datafile's time indexes get plotted asynchronously.
        and_the_newest_for_each_wave = next_few_days_of_wave_overlays.values('definition_id', 'applies_at_datetime')\
            .annotate(newest_id=Max('id'))
        wave_ids = and_the_newest_for_each_wave.values_list('newest_id', flat=True)

        and_the_newest_for_each_sst = next_few_days_of_sst_overlays.values('definition_id', 'applies_at_datetime')\
            .annotate(newest_id=Max('id'))
        sst_ids = and_the_newest_for_each_sst.values_list('newest_id', flat=True)

        # Filter out only the most recent overlay for each type and time
        newest_sst_overlays_to_display = next_few_days_of_sst_overlays.filter(id__in=sst_ids).order_by('definition', 'applies_at_datetime')
        newest_wave_overlays_to_display = next_few_days_of_wave_overlays.filter(id__in=wave_ids).order_by('definition', 'applies_at_datetime')

        wave_dates = newest_wave_overlays_to_display.values('applies_at_datetime')
        sst_dates = newest_sst_overlays_to_display.values('applies_at_datetime')

        #Get the dates where there is an SST, currents, and wave overlay
        date_overlap = Overlay.objects.filter(applies_at_datetime__in=sst_dates).filter(applies_at_datetime__in=wave_dates).values('applies_at_datetime')

        # Now get the actual overlays where there is an overlap
        overlapped_sst_items_to_display = newest_sst_overlays_to_display.filter(applies_at_datetime__in=date_overlap)
        overlapped_wave_items_to_display = newest_wave_overlays_to_display.filter(applies_at_datetime__in=date_overlap)

        #Join the two sets
        all_items_to_display = overlapped_sst_items_to_display | overlapped_wave_items_to_display

        return all_items_to_display


    # these are for getting and running task groups
    @classmethod
    def make_all_base_plots_for_next_few_days(cls):
        job = group(cls.get_tasks_for_base_plots_for_next_few_days())
        results = job.apply_async()
        return results

    @classmethod
    def get_tasks_for_all_base_plots(cls, time_index=0, file_id=None):
        #Add the SST and currents plot commands
        task_list = [cls.make_plot.s(od_id, time_index, file_id, immutable=True) for od_id in [1, 3]]

        #Add the wave watch plot command
        task_list.append(cls.make_wave_watch_plot.s(4, time_index, file_id, immutable=True) )
        job = task_list
        return job


#PASSING IN: the file IDs of all the DataFiles stored in the database for next few days of forecasts.
    @classmethod
    def get_tasks_for_base_plots_in_files(cls, file_ids):
        task_list = []

        for fid in file_ids:
            datafile = DataFile.objects.get(pk=fid)

            #Wavewatch and SST/currents files use a separate Plot function.
            if datafile.file.name.startswith("OuterGrid"):
                plotter = WaveWatchPlotter(datafile.file.name)
                for t in xrange(0, 85):
                    # Only plot every 4th index to match up with the SST forecast
                    if t % 4 == 0:
                        task_list.append(cls.make_wave_watch_plot.subtask(args=(4, t, fid), immutable=True) )

            else:
                plotter = Plotter(datafile.file.name)
                number_of_times = plotter.get_number_of_model_times()   # yeah, loading the plotter just for this isn't ideal...

                #make_plot needs to be called once for each time range
                for t in xrange(number_of_times):
                    #using EXTEND because we are adding multiple items: might also be able to use APPEND
                    task_list.extend(cls.make_plot.subtask(args=(od_id, t, fid), immutable=True) for od_id in [1, 3])
        return task_list


    @classmethod
    def get_tasks_for_base_plots_for_next_few_days(cls):
        file_ids = [datafile.id for datafile in DataFileManager.get_next_few_days_files_from_db()]
        return cls.get_tasks_for_base_plots_in_files(file_ids)

    @classmethod
    def delete_old_files(cls):
        how_old_to_keep = timezone.datetime.now()-timedelta(days=HOW_LONG_TO_KEEP_FILES)

        # UNCHOPPED database files
        old_unchopped_files = Overlay.objects.filter(applies_at_datetime__lte=how_old_to_keep)


        # the Overlay class has a custom delete method that deletes the overlay's
        #TILES, KEYS, and OVERLAY images from the disk.
        for eachfile in old_unchopped_files:
            Overlay.delete(eachfile)

        return True


    @staticmethod
    @shared_task(name='pl_plot.make_wave_watch_plot')
    def make_wave_watch_plot(overlay_definition_id, time_index=0, file_id =None):
        overlay_ids = []

        #grab the latest forecast file
        if file_id is None:
            datafile = DataFile.objects.latest('generated_datetime')
        else:
            datafile = DataFile.objects.get(pk=file_id)

        overlay_definition = OverlayDefinition.objects.get(pk=overlay_definition_id)

        generated_datetime = datafile.generated_datetime.date().strftime('%m_%d_%Y')

        #get the the number of forecasts contained in the netCDF
        datafile_read_object = netcdf_file(os.path.join(settings.MEDIA_ROOT, settings.WAVE_WATCH_DIR, datafile.file.name))
        all_forecasts = datafile_read_object.variables['HTSGW_surface'][:, :, :]

        #obtain how many forecast are contained in the netcdf
        #as of right now there are 85
        lengths = numpy.shape(all_forecasts)
        number_of_forecasts = lengths[0] #netCDF gives a 3D array (number of forecasts, latitudes, longitudes)

        #returns a netcdf file object with read mode
        plotter = WaveWatchPlotter(datafile.file.name)

        #Here is code in case you want to save the overlays in a separate folder. Recommend saving them all
        # in the UNCHOPPED folder however.
        #new_dir = settings.MEDIA_ROOT + settings.WAVE_WATCH_STORAGE_DIR + "/" + "Wave_Height_Forecast_" + generated_datetime
        #if not os.path.exists(new_dir):
            #os.makedirs(new_dir)
            #os.chmod(new_dir,0o777)
        #wave_storage_dir = settings.WAVE_WATCH_STORAGE_DIR + "/" + "Wave_Height_Forecast_" + generated_datetime


        #the forecast applies at some number of hours past the generated datetime.
        #plus NOON: so we need to add 5. Something is off with the datetime.
        applies_at_datetime = datafile.generated_datetime + timedelta(hours=time_index) + timedelta(hours=5)

        #Set a new tile directory name for each forecast_index
        tile_dir = "tiles_{0}_{1}".format(overlay_definition.function_name, uuid4())
        #print "tile_dir name = ", tile_dir

        #return overlaydefinition object; 4 is for wave watch
        overlay_definition = OverlayDefinition.objects.get(pk=overlay_definition_id)


        plot_filename, key_filename = plotter.make_plot(getattr(plot_functions, overlay_definition.function_name),
                        forecast_index=time_index, storage_dir=settings.UNCHOPPED_STORAGE_DIR,
                        generated_datetime=generated_datetime)

        overlay = Overlay(
            file=os.path.join(settings.UNCHOPPED_STORAGE_DIR, plot_filename),
            key=os.path.join(settings.KEY_STORAGE_DIR, key_filename),
            created_datetime=timezone.now(),
            applies_at_datetime=applies_at_datetime,
            tile_dir = tile_dir,
            zoom_levels = None,
            is_tiled = False,
            definition_id=overlay_definition_id,
        )
        overlay.save()
        overlay_ids.append(overlay.id)

        # # This code was used to view what is contained in the netCDF file
        # file = netcdf_file(os.path.join(settings.MEDIA_ROOT, settings.WAVE_WATCH_DIR, datafile.file.name))
        # variable_names_in_file = file.variables.keys()
        # print variable_names_in_file
        # # This prints all the wave height data
        # file.variables['HTSGW_surface'][:]
        # # This prints the dimensions of the wave height data
        # value = numpy.shape(file.variables['HTSGW_surface'][:])
        return overlay_ids

    @staticmethod
    @shared_task(name='pl_plot.make_plot')
    def make_plot(overlay_definition_id, time_index=0, file_id=None):
        zoom_levels_for_currents = [('2-7', 4), ('8-10', 2)]  # Team 1 says this is a hack. Team 2 is unsure why it is a hack.
        zoom_levels_for_others = [(None, None)]

        if file_id is None:
            datafile = DataFile.objects.latest('model_date')
        else:
            datafile = DataFile.objects.get(pk=file_id)
        plotter = Plotter(datafile.file.name)
        overlay_definition = OverlayDefinition.objects.get(pk=overlay_definition_id)

        if overlay_definition_id == 3:
            zoom_levels = zoom_levels_for_currents
        else:
            zoom_levels = zoom_levels_for_others

        tile_dir = "tiles_{0}_{1}".format(overlay_definition.function_name, uuid4())
        overlay_ids = []
        for zoom_level in zoom_levels:
            plot_filename, key_filename = plotter.make_plot(getattr(plot_functions, overlay_definition.function_name),
                                                            time_index=time_index, downsample_ratio=zoom_level[1])

            overlay = Overlay(
                file=os.path.join(settings.UNCHOPPED_STORAGE_DIR, plot_filename),
                key=os.path.join(settings.KEY_STORAGE_DIR, key_filename),
                created_datetime=timezone.now(),
                definition_id=overlay_definition_id,
                applies_at_datetime=plotter.get_time_at_oceantime_index(time_index),
                zoom_levels=zoom_level[0],
                tile_dir=tile_dir,
                is_tiled=False
            )
            overlay.save()
            overlay_ids.append(overlay.id)
        return overlay_ids


class OverlayDefinition(models.Model):
    OVERLAY_TYPES = (
        ('V', 'Vector'),
        ('FC', 'Filled Contour'),
    )
    type = models.CharField(max_length=4, choices=OVERLAY_TYPES)
        #it might turn out that these don't have to be unique
    display_name_long = models.CharField(max_length=240, unique=True)
    display_name_short = models.CharField(max_length=64)
    function_name = models.CharField(max_length=64, unique=True)
    is_base = models.BooleanField(default=False)


# this acts as a dictionary for the definition, so we can provide additional parameters.
class Parameters(models.Model):
    definition = models.ForeignKey(OverlayDefinition)
    key = models.CharField(max_length=240)
    value = models.CharField(max_length=240)


class Overlay(models.Model):
    definition = models.ForeignKey(OverlayDefinition)
    created_datetime = models.DateTimeField()
    file = models.ImageField(upload_to=settings.UNCHOPPED_STORAGE_DIR, null=True)
    tile_dir = models.CharField(max_length=240, null=True)
    key = models.ImageField(upload_to=settings.KEY_STORAGE_DIR, null=True)
    applies_at_datetime = models.DateTimeField(null=False)
    zoom_levels = models.CharField(max_length=50, null=True)
    is_tiled = models.BooleanField(default=False)

    #Custom delete method which will also delete the Overlay's image file from the disk and also the Key image and Tiles
    def delete(self,*args,**kwargs):

        #Delete the physical file from disk
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)

        #Delete the Key image
        if os.path.isfile(self.key.path):
            os.remove(self.key.path)

        directory=os.path.join('/opt/sharkeyes/media/tiles/', self.tile_dir)

        #TILES folder holds directories only. There are no Tile items in the database so we don't have to delete those.
        # Reference here:  http://stackoverflow.com/questions/2237909/delete-old-directories-in-python
        for r,d,f in os.walk(directory):
            for direc in d:
                try:
                    #delete the items recursively
                    shutil.rmtree(os.path.join(r, direc))

                except Exception,e:
                    print e
                    pass
        #then remove the tile directory itself
        try:
            shutil.rmtree(directory)

        except Exception,e:
            print e
            pass

        #Delete the actual model instance from the database
        super(Overlay, self).delete(*args,**kwargs)

# Function defined to allow dynamic path creation
# A new folder is created per forecast creation day that includes all the forecasts
def get_upload_path(instance,filename):
    return os.path.join(
        settings.WAVE_WATCH_STORAGE_DIR + "/" + "Wave_Height_Forecast_" + instance.created_datetime)


#note: Not using this right now.
# in future it will be better to use Overlay for all new models,
# rather than adding different types of overlays for each model.
class Wave_Watch_Overlay(models.Model):
    definition = models.ForeignKey(OverlayDefinition)
    created_datetime = models.DateTimeField()
    tile_dir = models.CharField(max_length=240, null=True)
    applies_at_datetime = models.DateTimeField(null=False)
    zoom_levels = models.CharField(max_length=50, null=True)
    is_tiled = models.BooleanField(default=False)
    #file = models.ImageField(upload_to=get_upload_path, null=True, max_length=500)      #get_upload_path was defined in order to allow for dynamic path creation
    key = models.ImageField(upload_to=settings.KEY_STORAGE_DIR, null=True)

