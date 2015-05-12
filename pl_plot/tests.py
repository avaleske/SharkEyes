from django.test import TestCase
from django.conf import settings
from scipy.io import netcdf_file
import os
from ftplib import FTP
from uuid import uuid4
from urlparse import urljoin
from datetime import datetime, timedelta
import urllib
from pl_download.models import get_ingria_xml_tree, extract_modified_datetime_from_xml
from django.utils import timezone

# Create your tests here.
import pl_plot
FILE_NAME = "ocean_his_3322_04-Feb-2014.nc"
CATALOG_XML_NAME = "catalog.xml"
XML_NAMESPACE = "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}"


class PlotterTestCase(TestCase):
    def setUp(self):
        None

    def test_netcdf_wave_format(self):
        print("Running Wave NetCDF Format Test: ")
        #directory of where files will be saved at
        destination_directory = os.path.join(settings.MEDIA_ROOT, settings.WAVE_WATCH_DIR)

        print "Downloading File"
        #file names might need to be created dynamically in the future if ftp site changes
        file_name = "outer.nc"

        #Connect to FTP site to get the file modification data
        ftp = FTP('cil-www.oce.orst.edu')
        ftp.login()

        #retrieve the ftp modified datetime format
        ftp_dtm = ftp.sendcmd('MDTM' + " /pub/outgoing/ww3data/" + file_name)

        #convert ftp datetime format to a string datetime
        modified_datetime = datetime.strptime(ftp_dtm[4:], "%Y%m%d%H%M%S").strftime("%Y-%m-%d")

        #Create File Name and Download actual File into media folder
        url = urljoin(settings.WAVE_WATCH_URL, file_name)
        filename = "{0}_{1}_{2}.nc".format("OuterGrid", modified_datetime, uuid4())
        urllib.urlretrieve(url=url, filename=os.path.join(destination_directory, filename))

        datafile_read_object = netcdf_file(os.path.join(settings.MEDIA_ROOT, settings.WAVE_WATCH_DIR, filename))
        print "Checking Variables: latitude, longitude, HTSGW_surface"
        surface = datafile_read_object.variables['HTSGW_surface'][:, :, :]
        long = datafile_read_object.variables['longitude'][:]
        lat = datafile_read_object.variables['latitude'][:]
        ftp.quit()
        self.assertIsNotNone(surface)
        self.assertIsNotNone(long)
        self.assertIsNotNone(lat)

    def test_netcdf_model_format(self):
        print("Running SST & Currents NetCDF Format Test:")
        #directory of where files will be saved at
        destination_directory = os.path.join(settings.MEDIA_ROOT, settings.NETCDF_STORAGE_DIR)
        filename = ""

        print "Get XML Tree from Site"
        tree = get_ingria_xml_tree()
        tags = tree.iter(XML_NAMESPACE + 'dataset')

        files_to_retrieve = []

        # download new file for next few days
        days_to_retrieve = [timezone.now().date(),
                            timezone.now().date()+timedelta(days=1),
                            timezone.now().date()+timedelta(days=2),
                            timezone.now().date()+timedelta(days=3)]

        print "Retrieve Files"
        for elem in tags:
            server_filename = elem.get('name')
            if not server_filename.startswith('ocean_his'):
                continue
            date_string_from_filename = server_filename.split('_')[-1]
            model_date = datetime.strptime(date_string_from_filename, "%d-%b-%Y.nc").date()   # this could fail, need error handling badly
            modified_datetime = extract_modified_datetime_from_xml(elem)
            for day_to_retrieve in days_to_retrieve:
                if model_date - day_to_retrieve == timedelta(days=0):
                    files_to_retrieve.append((server_filename, model_date, modified_datetime))

        for server_filename, model_date, modified_datetime in files_to_retrieve:
            url = urljoin(settings.BASE_NETCDF_URL, server_filename)
            filename = "{0}_{1}.nc".format(model_date, uuid4())
            print "Retrieving" + filename
            urllib.urlretrieve(url=url, filename=os.path.join(destination_directory, filename)) # this also needs a try/catch

        datafile_read_object = netcdf_file(os.path.join(settings.MEDIA_ROOT, settings.NETCDF_STORAGE_DIR, filename))
        print "Checking Variables: latitude, longitude, HTSGW_surface"
        long = datafile_read_object.variables['lon_rho'][0, :]
        lat = datafile_read_object.variables['lat_rho'][:, 0]
        self.assertIsNotNone(long)
        self.assertIsNotNone(lat)

    #def test_make_plot(self, oid=1, time_index=0, datafile=None):
        #print("Running Plot Test for SS Temperature: ")
        #return pl_plot.OverlayManager.make_plot(oid, time_index, datafile)

    #def test_plotter_can_plot(self):
        #print("Running Plot Test")
        #plotter = pl_plot.Plotter(  FILE_NAME)
        #data_file = plotter.load_file(FILE_NAME)
        #plotter.make_plot(data_file, pl_plot.plot_functions.sst_method())
