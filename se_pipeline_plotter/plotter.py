__author__ = 'avaleske'
from scipy.io import netcdf
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os

#definitely a temporary option
NETCDF_STORAGE_DIR = "/home/vagrant/generated_files/netcdf"
UNCHOPPED_STORAGE_DIR = "/home/vagrant/generated_files/unchopped"

FILE_NAME = "ocean_his_3322_04-Feb-2014.nc"


class Plotter:
    data_file = None

    def __init__(self):
        pass

    def load_file(self, file_name):
        #file_name = FILE_NAME;
        data_file = netcdf.netcdf_file(os.path.join(NETCDF_STORAGE_DIR, file_name))
        return data_file

    def make_plot(self, data_file, plot_method):
        fig = plt.figure()
        ax = fig.add_subplot(111)  # one subplot in the figure

        longs = data_file.variables['lon_rho'][0, :]
        lats = data_file.variables['lat_rho'][:, 0]

        # window cropped by picking lat and lon corners
        bmap = Basemap(projection='merc',
                       resolution='h', area_thresh=1.0,
                       llcrnrlat=lats[0], urcrnrlat=lats[-1],
                       llcrnrlon=longs[0], urcrnrlon=longs[-1],
                       ax=ax)

        plot_method(ax, data_file, bmap)
        fig.savefig(os.path.join(UNCHOPPED_STORAGE_DIR, 'out.png'),
                    dpi=800, bbox_inches='tight', pad_inches=0,
                    transparent=True, frameon=False)
        plt.close(fig)