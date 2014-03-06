__author__ = 'avaleske'
from scipy.io import netcdf
import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os

#definitely a temporary option
NETCDF_STORAGE_DIR = "/home/vagrant/static_files/netcdf"


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
        longitude = data_file.variables['lon_rho'][0]

        #latitude = [lon_list[0] for lon_list in f.variables['lat_rho']]
        latitude = data_file.variables['lat_rho'][0, :]

        temp_map = Basemap(projection='merc', resolution='h', area_thresh=1.0,
                   llcrnrlat=latitude[0], llcrnrlon=longitude[0],
                   urcrnrlat=latitude[-1], urcrnrlon=longitude[-1])