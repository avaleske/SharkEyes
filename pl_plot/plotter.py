__author__ = 'avaleske'
from scipy.io import netcdf
from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap
import os
from uuid import uuid4
from django.conf import settings


class Plotter:
    data_file = None

    def __init__(self, file_name):
        self.load_file(file_name)

    # todo: after the download pipeline step is done, convert this to grab the
    # filename from the database.
    def load_file(self, file_name):
        self.data_file = netcdf.netcdf_file(
            os.path.join(
                settings.MEDIA_ROOT,
                settings.NETCDF_STORAGE_DIR,
                file_name
            )
        )

    def make_plot(self, plot_function):
        fig = pyplot.figure()
        ax = fig.add_subplot(111)  # one subplot in the figure

        longs = self.data_file.variables['lon_rho'][0, :]
        lats = self.data_file.variables['lat_rho'][:, 0]

        # window cropped by picking lat and lon corners
        bmap = Basemap(projection='merc',
                       resolution='h', area_thresh=1.0,
                       llcrnrlat=lats[0], urcrnrlat=lats[-1],
                       llcrnrlon=longs[0], urcrnrlon=longs[-1],
                       ax=ax)

        plot_function(ax, self.data_file, bmap)

        filename = "{0}-{1}.png".format(plot_function.__name__, uuid4())

        dest = os.path.join(settings.MEDIA_ROOT, settings.UNCHOPPED_STORAGE_DIR)
        if not os.path.exists(dest):
            os.makedirs(dest)

        fig.savefig(
            os.path.join(dest, filename),
            dpi=800, bbox_inches='tight', pad_inches=0,
            transparent=True, frameon=False)
        pyplot.close(fig)

        return filename