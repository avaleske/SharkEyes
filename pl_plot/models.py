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
        # starts with "current" overlay, which is the closest to now, forward or backwards, and goes forward 4 days or
        # however far we have data, whichever is less
        # here assuming that the primary keys for the overlays are only monotonically increasing
        # and that the newer one is better.

        # should be okay that it doesn't know about zoom levels, since they should have the same tile_directory


        #now the Overlays should include WaveWatch items as well
        #This is probably where you could select Past items: the -timedelta could go back a few days rather than just 2 hours.

        next_few_days_of_overlays = Overlay.objects.filter(
            applies_at_datetime__gte=timezone.now()-timedelta(hours=2),
            applies_at_datetime__lte=timezone.now()+timedelta(days=4)
        )

        that_are_tiled = next_few_days_of_overlays.filter(is_tiled=True)

        and_the_newest_for_each = that_are_tiled.values('definition', 'applies_at_datetime')\
            .annotate(newest_id=Max('id'))
        ids_of_these = and_the_newest_for_each.values_list('newest_id', flat=True)

        overlays_to_display = Overlay.objects.filter(id__in=ids_of_these).order_by('definition', 'applies_at_datetime')

        # Team 1 says: filtering out the non-base ones, for now, because the javascript that displays the menu is hacky.
        return overlays_to_display.filter(definition__is_base=True)


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
        task_list.append(cls.make_wave_watch_plot.s(4, file_id, immutable=True) )
        job = task_list
        return job


#PASSING IN: the file IDs of all the DataFiles stored in the database for next few days of forecasts.
    @classmethod
    def get_tasks_for_base_plots_in_files(cls, file_ids):
        task_list = []

        for fid in file_ids:
            datafile = DataFile.objects.get(pk=fid)

            #NOTE: team 2 says determining what type of datafile it is based only on fileNAME is sort of hacky.
            #May want to refactor: e.g. add a "model_type" to the DataFile class which says if it
            #is a WaveWatch file or SST/Currents file.
            #print "datafile name:", datafile.file.name
            if datafile.file.name.startswith("OuterGrid"):
                plotter = WaveWatchPlotter(datafile.file.name)
                #TODO refactor to improve performance: change make_wave_watch_plot to only do 1 time_index at a time
                task_list.append(cls.make_wave_watch_plot.subtask(args=(4, fid), immutable=True) )

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
        # this will delete wavewatch overlays too
        old_unchopped_files = Overlay.objects.filter(applies_at_datetime__lte=how_old_to_keep)

        for eachfile in old_unchopped_files:
            #Delete the overlay from DB, its image from disk, and its key image from disk, using the custom delete() method
            Overlay.delete(eachfile)

        return True


    @staticmethod
    @shared_task(name='pl_plot.make_wave_watch_plot')
    def make_wave_watch_plot(overlay_definition_id, file_id =None):
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

        new_dir = settings.MEDIA_ROOT + settings.WAVE_WATCH_STORAGE_DIR + "/" + "Wave_Height_Forecast_" + generated_datetime
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            os.chmod(new_dir,0o777)
        wave_storage_dir = settings.WAVE_WATCH_STORAGE_DIR + "/" + "Wave_Height_Forecast_" + generated_datetime



#TODO refactor to improve performance: change make_wave_watch_plot be called with the time_index to plot at,
        #rather than doing all of the number_of_forecasts plots in the make_wave_watch_plot function.

#for forecast_index in range(0, number_of_forecasts):
        for forecast_index in range(0, number_of_forecasts):
            #the forecast applies at some number of hours past the generated datetime.
            #plus NOON: so we need to add 5. Something is off with the datetime.
            #applies_at_datetime = datafile.generated_datetime + timedelta(hours=forecast_index) + timedelta(hours=5)
            applies_at_datetime = datafile.generated_datetime + timedelta(hours=forecast_index) + timedelta(hours=5)
            print "applies at", applies_at_datetime

            #Need to set a new tile directory name for each forecast_index
            tile_dir = "tiles_{0}_{1}".format(overlay_definition.function_name, uuid4())
            print "tile_dir name = ", tile_dir

            #return overlaydefinition object; 4 is for wave watch
            overlay_definition = OverlayDefinition.objects.get(pk=overlay_definition_id)

#for zoom_level in zoom_levels:
       #     plot_filename, key_filename = plotter.make_plot(getattr(plot_functions, overlay_definition.function_name),

            plot_filename, key_filename = plotter.make_plot(getattr(plot_functions, overlay_definition.function_name),
                                                             forecast_index=forecast_index, storage_dir=settings.UNCHOPPED_STORAGE_DIR,
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
        zoom_levels_for_currents = [('2-7', 4), ('8-10', 2)]  # todo fix hacky hack for expo
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




    @classmethod
    def delete_old_files(cls):


        how_old_to_keep = timezone.datetime.now()-timedelta(days=HOW_LONG_TO_KEEP_FILES)

        # UNCHOPPED database files
        # this will delete wavewatch overlays too
        old_unchopped_files = Overlay.objects.filter(applies_at_datetime__lte=how_old_to_keep)
        #print " database: unchopped files to delete: "
        for eachfile in old_unchopped_files:
             print eachfile
             eachfile.delete()



        return True



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

    #Custom delete method which will also delete the Overlay's image file from the disk and also the Key image
    def delete(self,*args,**kwargs):

        if os.path.isfile(self.file.path):
            #Delete the physical file from disk
            os.remove(self.file.path)

        #Delete the Key image
        if os.path.isfile(self.key.path):
            os.remove(self.key.path)

        #Delete the model instance
        super(Overlay, self).delete(*args,**kwargs)

# Function defined to allow dynamic path creation
# A new folder is created per forecast creation day that includes all the forecasts
def get_upload_path(instance,filename):
    return os.path.join(
        settings.WAVE_WATCH_STORAGE_DIR + "/" + "Wave_Height_Forecast_" + instance.created_datetime)


#note: Note using this right not.
# in future it will be better to use Overlay for all new models,
# rather than adding different types of overlays for each model.
class Wave_Watch_Overlay(models.Model):
    definition = models.ForeignKey(OverlayDefinition)
    created_datetime = models.DateTimeField()


    tile_dir = models.CharField(max_length=240, null=True)
    #todo set nullable on the AppliesAt back to false, once we have set up the variable initialization.
    applies_at_datetime = models.DateTimeField(null=True)
    zoom_levels = models.CharField(max_length=50, null=True)
    is_tiled = models.BooleanField(default=False)
    #file = models.ImageField(upload_to=get_upload_path, null=True, max_length=500)      #get_upload_path was defined in order to allow for dynamic path creation
    key = models.ImageField(upload_to=settings.KEY_STORAGE_DIR, null=True)

