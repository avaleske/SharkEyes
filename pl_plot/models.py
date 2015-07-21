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
import numpy as np
import datetime

# This is how long old files (overlay items in the database, and corresponding items in UNCHOPPED folder)
HOW_LONG_TO_KEEP_FILES = 5


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
#TODO put in the ISBASE
        #TODO set back to -time hours = 2
        next_few_days_of_overlays = Overlay.objects.filter(
            applies_at_datetime__gte=timezone.now()-timedelta(days=2),
            applies_at_datetime__lte=timezone.now()+timedelta(days=4),
            is_tiled=True,
        )

        next_few_days_of_sst_overlays = next_few_days_of_overlays.filter(definition_id__in=[1, 3])
        next_few_days_of_wave_overlays = next_few_days_of_overlays.filter(definition_id__in=[4, 6])

        print "sst overlays:"
        for each in next_few_days_of_sst_overlays:
            print each.applies_at_datetime

        print "wave overlays:"
        for each in next_few_days_of_wave_overlays:
            print each.applies_at_datetime

        # Get the newest overlay for each Model type and time. This assumes that for a certain model date,
        # a larger ID value
        # indicates a more recently-created (and hence more accurate) overlay.
        # Note that a higher ID does NOT by itself indicate a more recent MODEL date
        # because a datafile's time indexes get plotted asynchronously. I.e. tomorrow at 1 PM and tomorrow at 5 PM do not
        # get plotted in that order, but two days' past forecast for tomorrow 1 PM will always get plotted before
        # yesterday's forecast for tomorrow 1 PM.
        and_the_newest_for_each_wave = next_few_days_of_wave_overlays.values('definition_id', 'applies_at_datetime')\
            .annotate(newest_id=Max('id'))
        wave_ids = and_the_newest_for_each_wave.values_list('newest_id', flat=True)

        and_the_newest_for_each_sst = next_few_days_of_sst_overlays.values('definition_id', 'applies_at_datetime')\
            .annotate(newest_id=Max('id'))
        sst_ids = and_the_newest_for_each_sst.values_list('newest_id', flat=True)

        # Filter out only the most recent overlay for each type and time
        newest_sst_overlays_to_display = next_few_days_of_sst_overlays.filter(id__in=sst_ids).order_by('definition', 'applies_at_datetime')
        newest_wave_overlays_to_display = next_few_days_of_wave_overlays.filter(id__in=wave_ids).order_by('definition', 'applies_at_datetime')

        wave_dates = newest_wave_overlays_to_display.values_list( 'applies_at_datetime', flat=True)
        sst_dates = newest_sst_overlays_to_display.values_list( 'applies_at_datetime', flat=True)
        print "wave dates:", wave_dates
        print "sst_dates", sst_dates

        #Get the distinct dates where there is an SST, currents, and also a wave overlay
        date_overlap = next_few_days_of_overlays.filter(applies_at_datetime__in=list(sst_dates))\
            .filter(applies_at_datetime__in=list(wave_dates)).values_list('applies_at_datetime', flat=True).distinct()
        print "date overlap:"
        for each in date_overlap:
            print each


        # Now get the actual overlays where there is an overlap
        overlapped_sst_items_to_display = newest_sst_overlays_to_display.filter(applies_at_datetime__in=list(date_overlap))
        overlapped_wave_items_to_display = newest_wave_overlays_to_display.filter(applies_at_datetime__in=list(date_overlap))

        #Join the two sets
        all_items_to_display = overlapped_sst_items_to_display | overlapped_wave_items_to_display
        print "all items to display:"
        for each in all_items_to_display:
            print each

        # Send the items back to the SharkEyesCore/views.py file, which preps the main page to be loaded.
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

        #Add the commands to plot wave Height (4) and Direction (6)
        task_list.append(cls.make_wave_watch_plot.s(4, time_index, file_id, immutable=True))
        task_list.append(cls.make_wave_watch_plot.s(6, time_index, file_id, immutable=True))
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
                    # Only plot every 4th index to match up with the SST forecast.
                    # WaveWatch has forecasts for every hour but at this time we don't need them all.
                    if t % 4 == 0:
                        task_list.append(cls.make_wave_watch_plot.subtask(args=(4, t, fid), immutable=True))
                        task_list.append(cls.make_wave_watch_plot.subtask(args=(6, t, fid), immutable=True))

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

        # Overlay items from the database
        old_unchopped_files = Overlay.objects.filter(applies_at_datetime__lte=how_old_to_keep)

        # the Overlay class has a custom delete method that deletes the overlay's
        #TILES, KEYS, and OVERLAY images from the disk.
        for eachfile in old_unchopped_files:
            Overlay.delete(eachfile)

        return True


    @staticmethod
    def get_currents_data(forecast_index, file_id):
        datafile = DataFile.objects.get(pk=file_id)
        data_file = netcdf_file(os.path.join(settings.MEDIA_ROOT, settings.NETCDF_STORAGE_DIR, datafile.file.name))
        currents_u = data_file.variables['u'][forecast_index][29]
        currents_v = data_file.variables['v'][forecast_index][29]

        print "currents u:", 10.0*currents_u
        print "\n\n\ncurrents v:", 10.0*currents_v

    # Just a helper function so that you can examine the first forecast (latitude, longitude, and wave height)
    # from the NetCDF file. Pass in the file id of the WaveWatch NetCDF file you want to plot.
    @staticmethod
    def get_data(forecast_index, file_id):
        datafile = DataFile.objects.get(pk=file_id)
        file = netcdf_file(os.path.join(settings.MEDIA_ROOT, settings.WAVE_WATCH_DIR, datafile.file.name))
        variable_names_in_file = file.variables.keys()
        print variable_names_in_file

        all_day_height = file.variables['HTSGW_surface'][:, :, :]
        all_day_direction = file.variables['DIRPW_surface'][:,:,:]
        all_day_lat = file.variables['latitude'][:, :]
        all_day_long = file.variables['longitude'][:, :]
        all_day_times = file.variables['time'][:]
        #print "times: "
        #for each in all_day_times:
            #print each

        basetime = datetime.datetime(1970,1,1,0,0,0)

        # Check the first value of the forecast
        forecast_zero = basetime + datetime.timedelta(all_day_times[0]/3600.0/24.0,0,0)
        print(forecast_zero)

        directions = all_day_direction[forecast_index, ::10, :]
        directions_mod = 90.0 - directions + 180.0
        index = directions_mod > 180
        directions_mod[index] = directions_mod[index] - 360;

        index = directions_mod < -180;
        directions_mod[index] = directions_mod[index] + 360;

        U = 10.*np.cos(np.deg2rad(directions_mod))
        V = 10.*np.sin(np.deg2rad(directions_mod))
        print "U:", U[:10, :10]
        print "\n\n\n\n\n\n\nV:", V[:10, :10]

        #print "\n\n\n\n\n\n\n\nDIRECTION"
        #for each in directions:
            #print each

        #print "\n\n\n\n\n\n\n\nDIRECTIONS MODIFIED"
        #for each in directions_mod:
            #print each



    @staticmethod
    def time_help():
         print "timezone:", timezone.get_current_timezone()
         print "zone now: ", timezone.get_current_timezone()
         print "local time now:", timezone.localtime(timezone.now())  #this prints current PST time, with DST correct
         print "timezone now:", timezone.make_aware(timezone.now() , timezone.utc)  #this is the UTC version of right-now's time
         print "", timezone.is_naive(timezone.localtime(timezone.now()))


    @staticmethod
    @shared_task(name='pl_plot.make_wave_watch_plot')
    def make_wave_watch_plot(overlay_definition_id, time_index=0, file_id =None):
        # TODO set the zoom levels for the wave Direction, similar to currents
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

        # Setting the time for applies_at, based on the Time variable in the file.
        # The time variable is # of seconds since start of time epoch, so we convert to UTC
        all_day_times = datafile_read_object.variables['time'][:]
        basetime = datetime.datetime(1970,1,1,0,0,0)  # Jan 1, 1970

        # This is the first forecast: right now it is Noon (UTC) [~5 AM PST] on the day before the file was downloaded
        forecast_zero = basetime + datetime.timedelta(all_day_times[0]/3600.0/24.0,0,0)

        # Based on the time index, say that this date is UTC (make_aware)
        applies_at_datetime = timezone.make_aware(forecast_zero + timedelta(hours=time_index) , timezone.utc)

        #Set a new tile directory name for each forecast_index
        tile_dir = "tiles_{0}_{1}".format(overlay_definition.function_name, uuid4())

        #return overlaydefinition object; 4 is for wave watch
        overlay_definition = OverlayDefinition.objects.get(pk=overlay_definition_id)

        plot_filename, key_filename = plotter.make_plot(getattr(plot_functions, overlay_definition.function_name),
                        forecast_index=time_index, storage_dir=settings.UNCHOPPED_STORAGE_DIR,
                        generated_datetime=generated_datetime)

        overlay = Overlay(
            file=os.path.join(settings.UNCHOPPED_STORAGE_DIR, plot_filename),
            key=os.path.join(settings.KEY_STORAGE_DIR, key_filename),
            created_datetime=timezone.now(),  #saves UTC correctly in database
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
            # Make a plot with downsampling of 4, and with 2
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

