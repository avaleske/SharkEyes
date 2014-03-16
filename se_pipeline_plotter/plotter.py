__author__ = 'avaleske'
from scipy.io import netcdf
from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap
import os
import datetime
from django.conf import settings
from se_pipeline_plotter.models import Overlay, OverlayDefinition, OverlayManager

FILE_NAME = "ocean_his_3322_04-Feb-2014.nc"


class PlotManager():
    def make_all_base_plots(self):
        # todo find a way to not reload the netcdf file for every plot maybe?
        plotter = self.Plotter(FILE_NAME)

        for overlay_definition in OverlayManager.get_all_base_definitions():
            
            overlay = Overlay(overlay_definition=overlay_definition)
            overlay.date_created = datetime.datetime.now()
            overlay


class Plotter:
    data_file = None

    def __init__(self, file_name):
        self.load_file(file_name)

    # todo: after the download pipeline step is done, convert this to grab the
    # filename from the database.
    def load_file(self, file_name):
        self.data_file = netcdf.netcdf_file(os.path.join(settings.MEDIA_ROOT,
                                       settings.NETCDF_STORAGE_DIR, file_name))

    def start

    def make_plot(self, plot_method):
        overlay = Overlay()

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

        plot_method(ax, self.data_file, bmap)
        fig.savefig(os.path.join(settings.UNCHOPPED_STORAGE_DIR, 'out.png'),
                    dpi=800, bbox_inches='tight', pad_inches=0,
                    transparent=True, frameon=False)
        pyplot.close(fig)