__author__ = 'avaleske'
from scipy.io import netcdf
import numpy
from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap
from pydap.client import open_url
import os
from uuid import uuid4
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone


class WaveWatchPlotter:
    data_file = None

    def __init__(self, file_name):
        self.load_file(file_name)

    def load_file(self, file_name):
        #Gives a netcdf file object with default mode of reading permissions only
        self.data_file = netcdf.netcdf_file(
            os.path.join(
                settings.MEDIA_ROOT,
                settings.WAVE_WATCH_DIR,
                file_name
            )
        )

    # the unchopped file's index starts at noon: index = 0 and progresses throgh 85 forecasts, one per hour, for the next 85 hours.
   # def get_time_from_index_of_file(self, index):
     #   self.data_file.variables
     #   ocean_time_epoch = datetime(day=1, month=1, year=2005, hour=0, minute=0, second=0, tzinfo=timezone.utc)
      #  seconds_since_epoch = timedelta(seconds=self.data_file.variables['ocean_time'][index])
      #  return ocean_time_epoch + seconds_since_epoch

#make a plot, with the Function to use specified, the storage directory specified, and the Index (ie 0--85 forecasts)
# based on the title of the file
    def make_plot(self, plot_function, forecast_index,storage_dir, generated_datetime):

        fig = pyplot.figure()
        key_fig = pyplot.figure(facecolor=settings.OVERLAY_KEY_COLOR)

        ax = fig.add_subplot(111)  # one subplot in the figure

        key_ax = key_fig.add_axes([0.1, 0.2, 0.6, 0.05])

        longs = self.data_file.variables['longitude'][:]
        lats = self.data_file.variables['latitude'][:]

        # window cropped by picking lat and lon corners
        # We are using the Mercator projection, because that is what Google Maps wants. The inputs should
        # probably be just plain latitude and longitude, i.e. they should be in unprojected form when they are passed in.
        bmap = Basemap(projection='merc',                         #A cylindrical, conformal projection.
                       resolution='h', area_thresh=1.0,
                       llcrnrlat=lats[0][0], urcrnrlat=lats[-1][0],
                       llcrnrlon=longs[0][0], urcrnrlon=longs[-1][-1],
                      ax=ax, epsg=4326)


        # TODO this will call the correct function based on what type of definition this was called by
        plot_function(ax=ax, data_file=self.data_file, forecast_index=forecast_index, bmap=bmap, key_ax=key_ax)

        plot_filename = "{0}_{1}_{2}_{3}.png".format(plot_function.__name__,forecast_index,generated_datetime, uuid4())
        key_filename = "{0}_key_{1}_{2}.png".format(plot_function.__name__,generated_datetime, uuid4())


        fig.savefig(
             os.path.join(settings.MEDIA_ROOT, storage_dir, plot_filename),
             dpi=1200, bbox_inches='tight', pad_inches=0,
             transparent=True, frameon=False)
        pyplot.close(fig)

        key_fig.savefig(
                 os.path.join(settings.MEDIA_ROOT, settings.KEY_STORAGE_DIR, key_filename),
                 dpi=500, bbox_inches='tight', pad_inches=0,
                 transparent=True, facecolor=key_fig.get_facecolor())
        pyplot.close(key_fig)
        return plot_filename, key_filename

class WindPlotter:
    data_file = None

    def __init__(self, file_name):
        self.load_file(file_name)

    def load_file(self, file_name):
        #This should have some form of error handling as it can fail
        self.data_file = open_url(settings.WIND_URL)

    def get_number_of_model_times(self):
        return 12

    def make_plot(self, plot_function, forecast_index,storage_dir, generated_datetime, downsample_ratio=None):

        fig = pyplot.figure()
        key_fig = pyplot.figure(facecolor=settings.OVERLAY_KEY_COLOR)

        ax = fig.add_subplot(111)  # one subplot in the figure

        key_ax = key_fig.add_axes([0.1, 0.2, 0.6, 0.05])

        # window cropped by picking lat and lon corners
        bmap = Basemap(projection='merc',                         #A cylindrical, conformal projection.
                       resolution='h', area_thresh=1.0,
                       llcrnrlat=40.5833284543, urcrnrlat=47.4999927992,
                       llcrnrlon=-129, urcrnrlon=-123.7265625,
                       ax=ax, epsg=4326)

        plot_function(ax=ax, data_file=self.data_file, forecast_index=forecast_index, bmap=bmap, key_ax=key_ax, downsample_ratio=downsample_ratio)

        plot_filename = "{0}_{1}_{2}_{3}.png".format(plot_function.__name__,forecast_index,generated_datetime, uuid4())
        key_filename = "{0}_key_{1}_{2}.png".format(plot_function.__name__,generated_datetime, uuid4())


        fig.savefig(
             os.path.join(settings.MEDIA_ROOT, storage_dir, plot_filename),
             dpi=1200, bbox_inches='tight', pad_inches=0,
             transparent=True, frameon=False)
        pyplot.close(fig)

        if forecast_index == 0:
            key_fig.savefig(
                 os.path.join(settings.MEDIA_ROOT, settings.KEY_STORAGE_DIR, key_filename),
                 dpi=500, bbox_inches='tight', pad_inches=0,
                 transparent=True, facecolor=key_fig.get_facecolor())
        pyplot.close(key_fig)
        return plot_filename, key_filename

class Plotter:
    data_file = None

    def __init__(self, file_name):
        self.load_file(file_name)

    def load_file(self, file_name):
        self.data_file = netcdf.netcdf_file(
            os.path.join(
                settings.MEDIA_ROOT,
                settings.NETCDF_STORAGE_DIR,
                file_name
            )
        )

    def get_time_at_oceantime_index(self, index):
        #Team 1 says todo add checking of times here. there's only three furthest out file
        ocean_time_epoch = datetime(day=1, month=1, year=2005, hour=0, minute=0, second=0, tzinfo=timezone.utc)
        seconds_since_epoch = timedelta(seconds=self.data_file.variables['ocean_time'][index])
        return ocean_time_epoch + seconds_since_epoch

    def get_number_of_model_times(self):
        return numpy.shape(self.data_file.variables['ocean_time'])[0]



    def make_plot(self, plot_function, time_index=0, downsample_ratio=None): #todo hack for expo

        fig = pyplot.figure()
        key_fig = pyplot.figure(facecolor=settings.OVERLAY_KEY_COLOR)
        ax = fig.add_subplot(111)  # one subplot in the figure
        key_ax = key_fig.add_axes([0.1, 0.2, 0.6, 0.05]) # this might be bad for when we have other types of plots


        longs = self.data_file.variables['lon_rho'][0, :]
        lats = self.data_file.variables['lat_rho'][:, 0]

        # window cropped by picking lat and lon corners
        bmap = Basemap(projection='merc',
                       resolution='h', area_thresh=1.0,
                       llcrnrlat=lats[0], urcrnrlat=lats[-1],
                       llcrnrlon=longs[0], urcrnrlon=longs[-1],
                       ax=ax, epsg=4326)


        plot_function(ax=ax, data_file=self.data_file, time_index=time_index, bmap=bmap, key_ax=key_ax,
                      downsample_ratio=downsample_ratio) #todo this param is a hack for expo

        plot_filename = "{0}_{1}.png".format(plot_function.__name__, uuid4())
        key_filename = "{0}_key_{1}.png".format(plot_function.__name__, uuid4())

        fig.savefig(
            os.path.join(settings.MEDIA_ROOT, settings.UNCHOPPED_STORAGE_DIR, plot_filename),
            dpi=1200, bbox_inches='tight', pad_inches=0,
            transparent=True, frameon=False)
        pyplot.close(fig)

        key_fig.savefig(
            os.path.join(settings.MEDIA_ROOT, settings.KEY_STORAGE_DIR, key_filename),
            dpi=500, bbox_inches='tight', pad_inches=0,
            transparent=True, facecolor=key_fig.get_facecolor())
        pyplot.close(key_fig)

        return plot_filename, key_filename
