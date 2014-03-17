__author__ = 'avaleske'
import numpy

# When you add a new function, add it as a new function definition to fixtures/initial_data.json

NUM_COLOR_LEVELS = 20


def sst_function(ax, data_file, bmap):
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
        contour_range_inc = (max_temp - min_temp) / NUM_COLOR_LEVELS
        color_levels = []
        for i in xrange(NUM_COLOR_LEVELS):
            color_levels.append(min_temp + i * contour_range_inc)

        overlay1 = bmap.contourf(x, y, surface_temp, color_levels, ax=ax)


def testtest():
    print("Yay!")