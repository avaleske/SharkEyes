__author__ = 'avaleske'
import numpy
from matplotlib import pyplot
import math

# When you add a new function, add it as a new function definition to fixtures/initial_data.json

NUM_COLOR_LEVELS = 20


def sst_function(ax, data_file, bmap, key_ax):
    # temperature has dimensions ('ocean_time', 's_rho', 'eta_rho', 'xi_rho')
    # s_rho corresponds to layers, of which there are 30, so we take the top one.
    surface_temp = data_file.variables['temp'][0][29]

    min_temp = numpy.amin(surface_temp)

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
    # is there an integer division issue we need to think about here?
    high_temp_range = math.ceil(max_temp)
    low_temp_range = math.floor(min_temp)
    contour_range_inc = (high_temp_range - low_temp_range) / NUM_COLOR_LEVELS
    color_levels = []
    for i in xrange(NUM_COLOR_LEVELS):
        color_levels.append(low_temp_range + i * contour_range_inc)

    overlay = bmap.contourf(x, y, surface_temp, color_levels, ax=ax)

    # add colorbar.
    cbar = pyplot.colorbar(overlay, orientation='horizontal', cax=key_ax)
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label('Celsius')


def salt_function(ax, data_file, bmap, key_ax):
    salt = data_file.variables["salt"][:]
    salt_layer = salt[0][29]
    min_salt = numpy.amin(salt_layer)
    max_salt = -100
    for i in xrange(250):
        for j in xrange(136):
            if max_salt < salt_layer[i][j] < 100:
                max_salt = salt_layer[i][j]

    longs, lats = bmap.makegrid(salt_layer.shape[1], salt_layer.shape[0])
    x, y = bmap(longs, lats)

    contour_range_inc = (math.ceil(max_salt) - math.floor(min_salt)) / NUM_COLOR_LEVELS
    print contour_range_inc
    color_levs = []
    for i in xrange(NUM_COLOR_LEVELS):
        color_levs.append(math.floor(min_salt) + i*contour_range_inc)

    overlay = bmap.contourf(x, y, salt_layer, color_levs, ax=ax)

     # add colorbar.
    cbar = pyplot.colorbar(overlay, orientation='horizontal', cax=key_ax)
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label('Salinity add units')


def testtest():
    print("Yay!")
