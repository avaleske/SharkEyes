import numpy
from matplotlib import pyplot
import math
from scipy import ndimage
import scipy

# When you add a new function, add it as a new function definition to fixtures/initial_data.json

NUM_COLOR_LEVELS = 20


def sst_function(ax, data_file, bmap, key_ax, time_index):
    def celius_to_fahrenheit(temp):
        if temp > 100:
            return numpy.nan
        else:
            return temp * 1.8 + 32
    vectorized_conversion = numpy.vectorize(celius_to_fahrenheit)

    # temperature has dimensions ('ocean_time', 's_rho', 'eta_rho', 'xi_rho')
    # s_rho corresponds to layers, of which there are 30, so we take the top one.
    rho_mask = data_file.variables['mask_rho'][:]
    surface_temp = vectorized_conversion(data_file.variables['temp'][time_index][29])
    #surface_temp[rho_mask == 0] = numpy.nan # mask out of range values
    longs = data_file.variables['lon_rho'][:]
    lats = data_file.variables['lat_rho'][:]

    min_temp = numpy.nanmin(surface_temp)
    max_temp = numpy.nanmax(surface_temp)
    print(min_temp, max_temp)

    x, y = bmap(longs, lats)

    # calculate and plot colored contours for TEMPERATURE data

    high_temp_range = math.ceil(max_temp)
    low_temp_range = math.floor(min_temp)
    contour_range_inc = (high_temp_range - low_temp_range) / NUM_COLOR_LEVELS
    color_levels = []
    for i in xrange(NUM_COLOR_LEVELS+1):
        color_levels.append(low_temp_range + i * contour_range_inc)

    bmap.drawmapboundary(linewidth=0.0, ax=ax)
    overlay = bmap.contourf(x, y, surface_temp, color_levels, ax=ax, extend='both')

    # add colorbar.
    cbar = pyplot.colorbar(overlay, orientation='horizontal', cax=key_ax)
    cbar.ax.tick_params(labelsize=10)
    cbar.ax.xaxis.label.set_color('white')
    cbar.ax.xaxis.set_tick_params(labelcolor='white')

    labels = [item.get_text() for item in cbar.ax.xaxis.get_majorticklabels()]
    if '.' in labels[0]:
        endlabel = str(math.ceil(max_temp))
    else:
        endlabel = str(int(math.ceil(max_temp)))
    labels = numpy.append(labels, [endlabel])
    locs = cbar.ax.xaxis.get_majorticklocs()
    locs = numpy.append(locs, [1.0])
    cbar.ax.xaxis.set_ticks(locs)
    cbar.ax.xaxis.set_ticklabels(labels)

    cbar.set_label("Fahrenheit")


def salt_function(ax, data_file, bmap, key_ax, time_index):
    salt = data_file.variables['salt'][:]
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
    cbar.set_label("Salinity (PSU)")


def currents_function(ax, data_file, bmap, key_ax, time_index):
    def compute_average(array):
        avg = numpy.average(array)
        return numpy.nan if avg > 10**3 else avg

    currents_u = data_file.variables['u'][time_index][29]
    currents_v = data_file.variables['v'][time_index][29]
    rho_mask = numpy.array(data_file.variables['mask_rho'][:])

    # average nearby points to align grid, and add the edge column/row so it's the right size.
    right_column = currents_u[:, -1:]
    currents_u_adjusted = ndimage.generic_filter(scipy.hstack((currents_u, right_column)), compute_average, footprint=[[1], [1]], mode='reflect')
    bottom_row = currents_v[-1:, :]
    currents_v_adjusted = ndimage.generic_filter(scipy.vstack((currents_v, bottom_row)), compute_average, footprint=[[1], [1]], mode='reflect')

    # zoom
    zoom_level = 4
    u_zoomed = crop_and_downsample(currents_u_adjusted, zoom_level)
    v_zoomed = crop_and_downsample(currents_v_adjusted, zoom_level)
    rho_mask[rho_mask == 0] = numpy.nan
    rho_mask_zoomed = crop_and_downsample(rho_mask, zoom_level)
    longs = data_file.variables['lon_rho'][:]
    lats = data_file.variables['lat_rho'][:]
    longs_zoomed = crop_and_downsample(longs, zoom_level, False)
    lats_zoomed = crop_and_downsample(lats, zoom_level, False)

    u_zoomed[rho_mask_zoomed == 0] = numpy.nan
    v_zoomed[rho_mask_zoomed == 0] = numpy.nan

    x, y = bmap(longs_zoomed, lats_zoomed)

    bmap.drawmapboundary(linewidth=0.0, ax=ax)
    overlay = bmap.quiver(x, y, u_zoomed, v_zoomed, ax=ax, color='black')

    quiverkey = key_ax.quiverkey(overlay, 2.5, .5, 0.5*.5144, "0.5 knots", labelpos='S', labelcolor='white', color='white', labelsep=.5)
    quiverkey1 = key_ax.quiverkey(overlay, 5, .5, 1*.5144, "1 knot", labelpos='S', labelcolor='white', color='white', labelsep=.5)
    quiverkey2 = key_ax.quiverkey(overlay, 7.5, .5, 2*.5144, "2 knots", labelpos='S', labelcolor='white', color='white', labelsep=.5)
    key_ax.set_axis_off()


def crop_and_downsample(source_array, downsample_ratio, average=True):
    ys, xs = source_array.shape
    cropped_array = source_array[:ys - (ys % int(downsample_ratio)), :xs - (xs % int(downsample_ratio))]
    if average:
        zoomed_array = scipy.nanmean(numpy.concatenate([[cropped_array[i::downsample_ratio, j::downsample_ratio]
                                                     for i in range(downsample_ratio)]
                                                    for j in range(downsample_ratio)]), axis=0)
    else:
        zoomed_array = cropped_array[::downsample_ratio, ::downsample_ratio]
    return zoomed_array