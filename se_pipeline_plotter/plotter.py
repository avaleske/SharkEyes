__author__ = 'avaleske'
from scipy.io import netcdf
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os

#definitely a temporary option
NETCDF_STORAGE_DIR = "/home/vagrant/generated_files/netcdf"
UNCHOPPED_STORAGE_DIR = "/home/vagrant/generated_files/unchopped"
NUM_COLOR_LEVELS = 20


class Plotter:
    def __init__(self):
        None

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

    def temp_method(self, ax, data_file, bmap):
        # temperature has dimensions ('ocean_time', 's_rho', 'eta_rho', 'xi_rho')
        # s_rho corresponds to layers, of which there are 30, so we take the top one.
        surface_temp = data_file.variables['temp'][0][29]

        min_temp = np.amin(surface_temp)

        # umm... there is junk data at large value ranges, so numpy.amax
        # finds these junk values - here's a quick fix
        max_temp = -100
        for i in xrange(surface_temp.shape[0]):
            for j in xrange(surface_temp.shape[1]):
                if max_temp < surface_temp[i][j] < 100:
                    max_temp = surface_temp[i][j]

        # convert temperature data into format for our map
        # get lat/longs of ny by nx evenly space grid.
        # then compute map proj coordinates.
        longs, lats = bmap.makegrid(surface_temp.shape[1], surface_temp.shape[0])
        x, y = bmap(longs, lats)

        # calculate and plot colored contours for TEMPERATURE data
        contour_range_inc = (max_temp - min_temp) / NUM_COLOR_LEVELS
        color_levels = []
        for i in xrange(NUM_COLOR_LEVELS):
            color_levels.append(min_temp + i * contour_range_inc)

        overlay1 = bmap.contourf(x, y, surface_temp, color_levels, ax=ax)