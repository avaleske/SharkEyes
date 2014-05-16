__author__ = 'avaleske'
from scipy.io import netcdf
import numpy
from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap
import os
from uuid import uuid4
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone


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
        #todo add checking of times here. there's only three furthest out file
        ocean_time_epoch = datetime(day=1, month=1, year=2005, hour=0, minute=0, second=0, tzinfo=timezone.utc)
        seconds_since_epoch = timedelta(seconds=self.data_file.variables['ocean_time'][index])
        return ocean_time_epoch + seconds_since_epoch

    def get_number_of_model_times(self):
        return numpy.shape(self.data_file.variables['ocean_time'])[0]

    def make_plot(self, plot_function, time_index=0):
        fig = pyplot.figure()
        key_fig = pyplot.figure()
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

        plot_function(ax=ax, data_file=self.data_file, time_index=time_index, bmap=bmap, key_ax=key_ax)

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
            transparent=True)
        pyplot.close(key_fig)

        return plot_filename, key_filename
