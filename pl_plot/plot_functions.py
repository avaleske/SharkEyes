import numpy
from matplotlib import pyplot, colors
import math
from scipy import ndimage
import scipy
from mpl_toolkits.basemap import Basemap


# When you add a new function, add it as a new function definition to fixtures/initial_data.json

NUM_COLOR_LEVELS = 80


def get_rho_mask(data_file):
    rho_mask = numpy.logical_not(data_file.variables['mask_rho'][:])
    rho_mask[207:221, 133:135] = 1
    rho_mask[201:202, 133:135] = 1
    return rho_mask

# Wave Model Data Information:
# Wave Data comes in 3D arrays (number of forecasts, latitude, longitude)
# As of right now (March 15) there are 85 forecasts in each netCDF file from 12 pm onward by the hour
# Wave Heights are measured in meters
# Data points over 1000 usually mark land
def wave_function(ax, data_file, bmap, key_ax, forecast_index):

    #grab longitude and latitude from netCDF file
    longs = data_file.variables['longitude'][:]
    lats = data_file.variables['latitude'][:]

    #get the wave height data from netCDF file
    all_day = data_file.variables['HTSGW_surface'][:, :, :]

    #convert/mesh the latitude and longitude data into 2D arrays to be used by contourf below
    x,y = numpy.meshgrid(longs,lats)

    #obtain all forecasts
    #heights is measured in meters, if a data point is over 1000 meters it is either not valid or it represents land
    #so we are masking all data over 1000
    heights = numpy.ma.masked_greater(all_day[forecast_index][:][:], 1000)

    #get the max and min period wave period for the day: used to set color contours
    min_period = int(math.floor(numpy.amin(heights)))
    max_period = int(math.ceil(numpy.amax(numpy.ma.masked_greater(heights, 1000))))

    #Allocates colors to the data by setting the range of the data and by setting color increments
    contour_range = max_period - min_period
    contour_range_inc = float(contour_range)/NUM_COLOR_LEVELS
    color_levels = []
    for i in xrange(NUM_COLOR_LEVELS+1):
        color_levels.append(min_period+1 + i * contour_range_inc)

    #Fill the contours with the colors
    overlay = bmap.contourf(x, y, heights, color_levels, ax=ax, extend='both', cmap=get_modified_jet_colormap())

    #Create the color bar
    cbar = pyplot.colorbar(overlay, orientation='horizontal', cax=key_ax)
    cbar.ax.tick_params(labelsize=10)
    cbar.ax.xaxis.label.set_color('white')
    cbar.ax.xaxis.set_tick_params(labelcolor='white')

    #todo DIVISION by ZERO
    locations = numpy.arange(0, 1.01, 1.0/(NUM_COLOR_LEVELS))[::10]    # we just want every sixth label
    float_labels = numpy.arange(min_period, max_period + 0.01, contour_range_inc)[::10]
    labels = ["%.1f" % num for num in float_labels]
    cbar.ax.xaxis.set_ticks(locations)
    cbar.ax.xaxis.set_ticklabels(labels)
    cbar.set_label("Wave Height (m)")


def sst_function(ax, data_file, bmap, key_ax, time_index, downsample_ratio):
    def celsius_to_fahrenheit(temp):
        return temp * 1.8 + 32
    vectorized_conversion = numpy.vectorize(celsius_to_fahrenheit)

    # temperature has dimensions ('ocean_time', 's_rho', 'eta_rho', 'xi_rho')
    # s_rho corresponds to layers, of which there are 30, so we take the top one.
    surface_temp = numpy.ma.array(vectorized_conversion(data_file.variables['temp'][time_index][29]), mask=get_rho_mask(data_file))
        
    longs = data_file.variables['lon_rho'][:]
    lats = data_file.variables['lat_rho'][:]

    #get the max and min temps for the daytem
    all_day = data_file.variables['temp'][:, 29, :, :]
    min_temp = int(math.floor(celsius_to_fahrenheit(numpy.amin(all_day))))
    max_temp = int(math.ceil(celsius_to_fahrenheit(numpy.amax(numpy.ma.masked_greater(all_day, 1000)))))
    
    x, y = bmap(longs, lats)

    # calculate and plot colored contours for TEMPERATURE data
    # 21 levels, range from one over min to one under max, as the colorbar caps each have their color and will color
    # out of bounds data with their color.
    contour_range = ((max_temp - 1) - (min_temp + 1))
    contour_range_inc = float(contour_range)/NUM_COLOR_LEVELS
    color_levels = []
    for i in xrange(NUM_COLOR_LEVELS+1):
        color_levels.append(min_temp+1 + i * contour_range_inc)

    bmap.drawmapboundary(linewidth=0.0, ax=ax)
    overlay = bmap.contourf(x, y, surface_temp, color_levels, ax=ax, extend='both', cmap=get_modified_jet_colormap())

    # add colorbar.
    cbar = pyplot.colorbar(overlay, orientation='horizontal', cax=key_ax)
    cbar.ax.tick_params(labelsize=10)
    cbar.ax.xaxis.label.set_color('white')
    cbar.ax.xaxis.set_tick_params(labelcolor='white')

    locations = numpy.arange(0, 1.01, 1.0/(NUM_COLOR_LEVELS))[::10]    # we just want every 10th label
    float_labels = numpy.arange(min_temp, max_temp + 0.01, contour_range_inc)[::10]
    labels = ["%.1f" % num for num in float_labels]
    cbar.ax.xaxis.set_ticks(locations)
    cbar.ax.xaxis.set_ticklabels(labels)
    cbar.set_label("Fahrenheit")


def salt_function(ax, data_file, bmap, key_ax, time_index, downsample_ratio):
     # salt has dimensions ('ocean_time', 's_rho', 'eta_rho', 'xi_rho')
    # s_rho corresponds to layers, of which there are 30, so we take the top one.
    surface_salt = numpy.ma.array(data_file.variables['salt'][time_index][29], mask=get_rho_mask(data_file))

    longs = data_file.variables['lon_rho'][:]
    lats = data_file.variables['lat_rho'][:]

    #get the max and min salinity for the day
    all_day = data_file.variables['salt'][:, 29, :, :]
    min_salt = int(math.floor(numpy.amin(all_day)))
    max_salt = int(math.ceil(numpy.amax(numpy.ma.masked_greater(all_day, 1000))))

    x, y = bmap(longs, lats)

    # calculate and plot colored contours for salinity data
    # 21 levels, range from one over min to one under max, as the colorbar caps each have their color and will color
    # out of bounds data with their color.
    contour_range = ((max_salt - 1) - (min_salt + 1))
    contour_range_inc = float(contour_range)/NUM_COLOR_LEVELS

    color_levels = []
    for i in xrange(NUM_COLOR_LEVELS+1):
        color_levels.append(min_salt+1 + i * contour_range_inc)

    bmap.drawmapboundary(linewidth=0.0, ax=ax)
    overlay = bmap.contourf(x, y, surface_salt, color_levels, ax=ax, extend='both', cmap=get_modified_jet_colormap())

    # add colorbar.
    cbar = pyplot.colorbar(overlay, orientation='horizontal', cax=key_ax)
    cbar.ax.tick_params(labelsize=10)
    cbar.ax.xaxis.label.set_color('white')
    cbar.ax.xaxis.set_tick_params(labelcolor='white')

    locations = numpy.arange(0, 1.01, 1.0/(NUM_COLOR_LEVELS))[::3]    # we just want every third label
    float_labels = numpy.arange(min_salt, max_salt + 0.01, contour_range_inc)[::3]
    labels = ["%.1f" % num for num in float_labels]
    cbar.ax.xaxis.set_ticks(locations)
    cbar.ax.xaxis.set_ticklabels(labels)
    cbar.set_label("Salinity (PSU)")


def currents_function(ax, data_file, bmap, key_ax, time_index, downsample_ratio):
    def compute_average(array):
        avg = numpy.average(array)
        return numpy.nan if avg > 10**3 else avg

    currents_u = data_file.variables['u'][time_index][29]
    currents_v = data_file.variables['v'][time_index][29]
    rho_mask = get_rho_mask(data_file)

    # average nearby points to align grid, and add the edge column/row so it's the right size.
    right_column = currents_u[:, -1:]
    currents_u_adjusted = ndimage.generic_filter(scipy.hstack((currents_u, right_column)),
                                                 compute_average, footprint=[[1], [1]], mode='reflect')
    bottom_row = currents_v[-1:, :]
    currents_v_adjusted = ndimage.generic_filter(scipy.vstack((currents_v, bottom_row)),
                                                 compute_average, footprint=[[1], [1]], mode='reflect')

    # zoom
    u_zoomed = crop_and_downsample(currents_u_adjusted, downsample_ratio)
    v_zoomed = crop_and_downsample(currents_v_adjusted, downsample_ratio)
    rho_mask[rho_mask == 1] = numpy.nan
    rho_mask_zoomed = crop_and_downsample(rho_mask, downsample_ratio)
    longs = data_file.variables['lon_rho'][:]
    lats = data_file.variables['lat_rho'][:]
    longs_zoomed = crop_and_downsample(longs, downsample_ratio, False)
    lats_zoomed = crop_and_downsample(lats, downsample_ratio, False)

    u_zoomed[rho_mask_zoomed == 1] = numpy.nan
    v_zoomed[rho_mask_zoomed == 1] = numpy.nan

    x, y = bmap(longs_zoomed, lats_zoomed)

    print x
    print y

    bmap.drawmapboundary(linewidth=0.0, ax=ax)
    overlay = bmap.quiver(x, y, u_zoomed, v_zoomed, ax=ax, color='black')

    quiverkey = key_ax.quiverkey(overlay, .95, .4, 0.5*.5144, ".5 knots", labelpos='S', labelcolor='white',
                                 color='white', labelsep=.5, coordinates='axes')
    quiverkey1 = key_ax.quiverkey(overlay, 3.75, .4, 1*.5144, "1 knot", labelpos='S', labelcolor='white',
                                  color='white', labelsep=.5, coordinates='axes')
    quiverkey2 = key_ax.quiverkey(overlay, 6.5, .4, 2*.5144, "2 knots", labelpos='S', labelcolor='white',
                                  color='white', labelsep=.5, coordinates='axes')
    key_ax.set_axis_off()


def wind_function(ax, data_file, bmap, key_ax, forecast_index, downsample_ratio):
    def compute_average(array):
        avg = numpy.average(array)
        return numpy.nan if avg > 10**3 else avg

    #forecast_index+104 because there are 13 days of backcasts that we do not need
    winds_u = data_file['u-component_of_wind_height_above_ground'][forecast_index+104, 0, :, :]
    winds_v = data_file['v-component_of_wind_height_above_ground'][forecast_index+104, 0, :, :]

    #values come from the text file and allow you to convert from the model's coordinate projection system
    info = numpy.loadtxt('latlon.g218')
    lats = numpy.reshape(info[:, 2], [428,614])
    longs = numpy.reshape(info[:, 3], [428,614])
    #Cutting down plotting region
    lats = lats[233:311,100:250]
    longs = longs[233:311,100:250]

    for i in range (0, len(longs)):
        longs[i] = -longs[i]

    # average nearby points to align grid, and add the edge column/row so it's the right size.
    winds_u = numpy.reshape(winds_u, (428, 614))
    winds_u = winds_u[233:311,100:250]
    winds_v = numpy.reshape(winds_v, (428, 614))
    winds_v = winds_v[233:311,100:250]

    right_column = winds_u[:, -1:]
    winds_u_adjusted = ndimage.generic_filter(scipy.hstack((winds_u, right_column)),
                                                 compute_average, footprint=[[1], [1]], mode='reflect')
    bottom_row = winds_v[-1:, :]
    winds_v_adjusted = ndimage.generic_filter(scipy.vstack((winds_v, bottom_row)),
                                                compute_average, footprint=[[1], [1]], mode='reflect')

    #This is for calculating the different zoom levels
    u_zoomed = crop_and_downsample(winds_u_adjusted, 1)
    v_zoomed = crop_and_downsample(winds_v_adjusted, 1)

    longs_zoomed = crop_and_downsample(longs, 1, False)
    lats_zoomed = crop_and_downsample(lats, 1, False)


    x, y = bmap(longs_zoomed, lats_zoomed)

    u_zoomed = u_zoomed[:,:150]
    v_zoomed = v_zoomed[:78,:]

    bmap.drawmapboundary(linewidth=0.0, ax=ax)
    overlay = bmap.quiver(x, y, u_zoomed, v_zoomed, ax=ax, color='black')

    quiverkey = key_ax.quiverkey(overlay, .95, .4, 0.5*.5144, ".5 knots", labelpos='S', labelcolor='white',
                                 color='white', labelsep=.5, coordinates='axes')
    quiverkey1 = key_ax.quiverkey(overlay, 3.75, .4, 1*.5144, "1 knot", labelpos='S', labelcolor='white',
                                  color='white', labelsep=.5, coordinates='axes')
    quiverkey2 = key_ax.quiverkey(overlay, 6.5, .4, 2*.5144, "2 knots", labelpos='S', labelcolor='white',
                                  color='white', labelsep=.5, coordinates='axes')
    key_ax.set_axis_off()


def crop_and_downsample(source_array, downsample_ratio, average=True):
    ys, xs = source_array.shape
    cropped_array = source_array[:ys - (ys % int(downsample_ratio)), :xs - (xs % int(downsample_ratio))]
    if average:
        zoomed_array = scipy.nanmean(numpy.concatenate(
            [[cropped_array[i::downsample_ratio, j::downsample_ratio]
                                                     for i in range(downsample_ratio)]
                                                    for j in range(downsample_ratio)]), axis=0)
    else:
        zoomed_array = cropped_array[::downsample_ratio, ::downsample_ratio]
    return cropped_array


def get_modified_jet_colormap():
    modified_jet_cmap_dict = {
        'red': ((0., .15, .15),
                (0.05, .15, .15),
                (0.11, .1, .1),
                (0.2, 0, 0),
                (0.4, .3, .3),
                (0.5, .9, .9),
                (0.66, 1, 1),
                (0.89, 1, 1),
                (1, 0.5, 0.5)),
        'green': ((0., 0, 0),
                   (0.05, 0, 0),
                   (0.11, 0, 0),
                   (0.3, 0.4, 0.4),
                   (0.45, 1, 1),
                   (0.55, 1, 1),
                   (0.80, 0.2, 0.2),
                   (0.91, 0, 0),
                   (1, 0, 0)),
        'blue': ((0., 0.5, 0.5),
                  (0.05, 0.5, 0.5),
                  (0.11, .7, .7),
                  (0.34, 1, 1),
                  (0.5, .9, .9),
                  (0.75, 0, 0),
                  (1, 0, 0))
    }
    return colors.LinearSegmentedColormap('modified_jet', modified_jet_cmap_dict, 256)
