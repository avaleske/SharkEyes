__author__ = 'avaleske'
import numpy
from matplotlib import pyplot
import math
from scipy import ndimage
import scipy

# When you add a new function, add it as a new function definition to fixtures/initial_data.json

NUM_COLOR_LEVELS = 20


def sst_function(ax, data_file, bmap, key_ax, time_index):
    # temperature has dimensions ('ocean_time', 's_rho', 'eta_rho', 'xi_rho')
    # s_rho corresponds to layers, of which there are 30, so we take the top one.
    surface_temp = data_file.variables['temp'][time_index][29]
    longs = data_file.variables['lon_rho'][:]
    lats = data_file.variables['lat_rho'][:]

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
    #longs, lats = bmap.makegrid(surface_temp.shape[1], surface_temp.shape[0])
    x, y = bmap(longs, lats)

    # calculate and plot colored contours for TEMPERATURE data
    # is there an integer division issue we need to think about here?
    high_temp_range = math.ceil(max_temp)
    low_temp_range = math.floor(min_temp)
    contour_range_inc = (high_temp_range - low_temp_range) / NUM_COLOR_LEVELS
    color_levels = []
    for i in xrange(NUM_COLOR_LEVELS+1):
        color_levels.append(low_temp_range + i * contour_range_inc)

    bmap.drawmapboundary(linewidth=0.0, ax=ax)
    overlay = bmap.contourf(x, y, surface_temp, color_levels, ax=ax)

    # add colorbar.
    cbar = pyplot.colorbar(overlay, orientation='horizontal', cax=key_ax)
    cbar.ax.tick_params(labelsize=10)
    cbar.ax.xaxis.label.set_color('white')
    cbar.ax.xaxis.set_tick_params(labelcolor='white')
    cbar.set_label('Celsius')


def salt_function(ax, data_file, bmap, key_ax, time_index):
    salt = data_file.variables["salt"][:]
    salt_layer = salt[time_index][29]
    min_salt = numpy.amin(salt_layer)
    max_salt = -100
    for i in xrange(250):
        for j in xrange(136):
            if max_salt < salt_layer[i][j] < 100:
                max_salt = salt_layer[i][j]

    longs, lats = bmap.makegrid(salt_layer.shape[1], salt_layer.shape[0])
    x, y = bmap(longs, lats)

    contour_range_inc = (math.ceil(max_salt) - math.floor(min_salt)) / NUM_COLOR_LEVELS

    color_levs = []
    for i in xrange(NUM_COLOR_LEVELS+1):
        color_levs.append(math.floor(min_salt) + i*contour_range_inc)


    bmap.drawmapboundary(linewidth=0.0, ax=ax)
    overlay = bmap.contourf(x, y, salt_layer, color_levs, ax=ax, bbox_inches='tight', pad_inches=0)



     # add colorbar.
    cbar = pyplot.colorbar(overlay, orientation='horizontal', cax=key_ax)
    cbar.ax.tick_params(labelsize=10)
    cbar.ax.xaxis.label.set_color('white')
    cbar.ax.xaxis.set_tick_params(labelcolor='white')
    cbar.set_label('Salinity (PSU)')


def currents_function(ax, data_file, bmap, key_ax, time_index):
    def compute_average(array):
        avg = numpy.average(array)
        return numpy.nan if avg > 10**3 else avg

    currents_u = data_file.variables['u'][time_index][29]
    currents_v = data_file.variables['v'][time_index][29]
    u_mask = data_file.variables['mask_u'][:]
    v_mask = data_file.variables['mask_v'][:]
    rho_mask = data_file.variables['mask_rho'][:]

    # average nearby points to align grid, and add the edge column/row so it's the right size.
    right_column = currents_u[:, -1:]
    currents_u_adjusted = ndimage.generic_filter(scipy.hstack((currents_u, right_column)), compute_average, footprint=[[1], [1]], mode='reflect')
    bottom_row = currents_v[-1:, :]
    currents_v_adjusted = ndimage.generic_filter(scipy.vstack((currents_v, bottom_row)), compute_average, footprint=[[1], [1]], mode='reflect')

    # zoom
    zoom_level = 4
    ys, xs = currents_u_adjusted.shape
    u_cropped = currents_u_adjusted[:ys-(ys % int(zoom_level)), :xs-(xs % int(zoom_level))]
    v_cropped = currents_v_adjusted[:ys-(ys % int(zoom_level)), :xs-(xs % int(zoom_level))]
    u_zoomed = scipy.nanmean(numpy.concatenate([[u_cropped[i::zoom_level,j::zoom_level]
        for i in range(zoom_level)]
        for j in range(zoom_level)]), axis=0)
    v_zoomed = scipy.nanmean(numpy.concatenate([[v_cropped[i::zoom_level,j::zoom_level]
        for i in range(zoom_level)]
        for j in range(zoom_level)]), axis=0)


    rho_mask_cropped = numpy.array(rho_mask[:ys-(ys % int(zoom_level)), :xs-(xs % int(zoom_level))])
    rho_mask_cropped[rho_mask_cropped == 0] = numpy.nan
    rho_mask_zoomed = scipy.nanmean(numpy.concatenate([[rho_mask_cropped[i::zoom_level, j::zoom_level]
        for i in range(zoom_level)]
        for j in range(zoom_level)]), axis=0)
    #rho_mask_zoomed = rho_mask[::4, ::4]

    longs, lats = bmap.makegrid(u_zoomed.shape[1], v_zoomed.shape[0])
    x, y = bmap(longs, lats)

    u_zoomed[rho_mask_zoomed == 0] = numpy.nan
    v_zoomed[rho_mask_zoomed == 0] = numpy.nan
    #print u_zoomed
    #print rho_mask_zoomed
    bmap.drawmapboundary(linewidth=0.0, ax=ax)
    #linewidths=(0.05,), edgecolors=('white')
    overlay = bmap.quiver(x, y, u_zoomed, v_zoomed, ax=ax, color='black')
    quiverkey = key_ax.quiverkey(overlay, 2.5, .5, 0.5*.5144, "0.5 knots", labelpos='S', labelcolor='white', color='white', labelsep=.5)
    quiverkey1 = key_ax.quiverkey(overlay, 5, .5, 1*.5144, "1 knot", labelpos='S', labelcolor='white', color='white', labelsep=.5)
    quiverkey2 = key_ax.quiverkey(overlay, 7.5, .5, 2*.5144, "2 knots", labelpos='S', labelcolor='white', color='white', labelsep=.5)
    key_ax.set_axis_off()

