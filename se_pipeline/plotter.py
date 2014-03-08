__author__ = 'avaleske'
from scipy.io import netcdf
import numpy, os
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

    def make_temp_plot(self, data_file):

         # temperature has dimensions ('ocean_time', 's_rho', 'eta_rho', 'xi_rho')
        # s_rho corresponds to layers, of which there are 30, so we take the top one.
        surface_temp = data_file.variables['temp'][0][29]

        #get lat and long
        longs = data_file.variables['lon_rho'][0, :]
        lats = data_file.variables['lat_rho'][:, 0]

        min_temp = numpy.amin(surface_temp)

        # umm... there is junk data at large value ranges, so numpy.amax
        # finds these junk values - here's a quick fix
        max_temp = -100
        for i in xrange(250):
            for j in xrange(136):
                if max_temp < surface_temp[i][j] < 100:
                    max_temp = surface_temp[i][j]

        print(len(lats))
        print(len(longs))
        print("max/min lon:", longs[0], longs[-1])
        print("max/min lat:", lats[0], lats[-1])

        # window cropped by picking lat and lon corners
        temp_map = Basemap(projection='merc',
                           resolution='h', area_thresh=1.0,
                           llcrnrlat=lats[0], urcrnrlat=lats[-1],
                           llcrnrlon=longs[0], urcrnrlon=longs[-1])

        # convert temperature data into format for our map
        longs, lats = temp_map.makegrid(
            surface_temp.shape[1], surface_temp.shape[0])   # get lat/lons of ny by nx evenly space grid.
        x, y = temp_map(longs, lats)                        # compute map proj coordinates.

        # calculate and plot colored contours for TEMPERATURE data
        contour_range_inc = (max_temp - min_temp)/NUM_COLOR_LEVELS
        color_levs = []
        for i in xrange(NUM_COLOR_LEVELS):
            color_levs.append(min_temp + i*contour_range_inc)
        overlay1 = temp_map.contourf(x, y, surface_temp, color_levs)
        print(type(overlay1))

        plt.savefig(os.path.join(UNCHOPPED_STORAGE_DIR, 'out.png'), dpi=800, bbox_inches='tight', pad_inches=0)

        '''


        # umm... there is junk data at large value ranges, so numpy.amax
        # finds these junk values - here's a quick fix
        max_temp = -100
        min_temp = numpy.amin(surface_temp)
        for i in xrange(len(longitude)):                #todo make these arange()
            for j in xrange(len(latitude)):
                if max_temp < surface_temp[i][j] < 100:
                    max_temp = surface_temp[i][j]

        #picking lat and long corners to crop window
        temp_map = Basemap(projection='merc', resolution='h', area_thresh=1.0,
                           llcrnrlat=latitude[0], llcrnrlon=longitude[0],
                           urcrnrlat=latitude[-1], urcrnrlon=longitude[-1])

        ny = surface_temp.shape[0]
        nx = surface_temp.shape[1]
        longs, lats = temp_map.makegrid(nx, ny)   # get lat/longs of ny by nx evenly space grid.
        x, y = temp_map(longs, lats)              # compute map proj coordinates.

        # calculate and plot colored contours for TEMPERATURE data
        num_levels = 20
        contour_range_inc = (max_temp - min_temp)/num_levels
        color_levs = []
        for i in xrange(num_levels):
            color_levs.append(min_temp + i*contour_range_inc)
        overlay1 = temp_map.contourf(x, y, surface_temp, color_levs)

        temp_map.drawcoastlines()
        temp_map.fillcontinents()
        plt.savefig('/home/vagrant/static_files/unchopped/temp.png', dpi=800, bbox_inches='tight', pad_inches=0)'''

        # make white transparent, while we are at it
        """tmp_img = Image.open('out.png')
        tmp_img = tmp_img.convert("RGBA")
        pixdata = tmp_img.load()
        for y in xrange(tmp_img.size[1]):
            for x in xrange(tmp_img.size[0]):
                if pixdata[x, y] == (255, 255, 255, 255):
                    pixdata[x, y] = (255, 255, 255, 0)
        tmp_img.save('out.png')"""