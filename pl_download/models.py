from django.db import models
from django.conf import settings
from celery import shared_task
from urlparse import urljoin
from django.utils import timezone
import urllib
import os
from uuid import uuid4
from urlparse import urljoin
import urllib2
from defusedxml import ElementTree
from datetime import datetime, timedelta
from dateutil import parser, tz
from django.db.models.aggregates import Max
from django.db.models import Q
from operator import __or__ as OR
from ftplib import FTP
from django.db import models
import shutil


CATALOG_XML_NAME = "catalog.xml"
XML_NAMESPACE = "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}"
HOW_LONG_TO_KEEP_FILES = 10


def get_ingria_xml_tree():
    # todo: need to handle if the xml file isn't available
    xml_url = urljoin(settings.BASE_NETCDF_URL, CATALOG_XML_NAME)
    catalog_xml = urllib2.urlopen(xml_url)
    tree = ElementTree.parse(catalog_xml)
    return tree


def extract_modified_datetime_from_xml(elem):
    modified_datetime_string = elem.find(XML_NAMESPACE + 'date').text
    naive_datetime = parser.parse(modified_datetime_string)  # the date in the xml file follows iso standards, so we're gold.
    modified_datetime = timezone.make_aware(naive_datetime, timezone.utc)
    return modified_datetime


class DataFileManager(models.Manager):
    # grabs file for next few days.
    # todo make each file download in a separate task
    @staticmethod
    @shared_task(name='pl_download.fetch_new_files')

    #FETCH FILES FOR CURRENTS AND SST
    def fetch_new_files():
        if not DataFileManager.is_new_file_to_download():
            return []

        # download new file for next few days
        days_to_retrieve = [timezone.now().date(),
                            timezone.now().date()+timedelta(days=1),
                            timezone.now().date()+timedelta(days=2),
                            timezone.now().date()+timedelta(days=3)]
        files_to_retrieve = []
        tree = get_ingria_xml_tree()    # yes, we just did this to see if there's a new file. refactor later.
        tags = tree.iter(XML_NAMESPACE + 'dataset')

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

        destination_directory = os.path.join(settings.MEDIA_ROOT, settings.NETCDF_STORAGE_DIR)

        new_file_ids = []

        for server_filename, model_date, modified_datetime in files_to_retrieve:
            url = urljoin(settings.BASE_NETCDF_URL, server_filename)
            local_filename = "{0}_{1}.nc".format(model_date, uuid4())
            urllib.urlretrieve(url=url, filename=os.path.join(destination_directory, local_filename)) # this also needs a try/catch

            datafile = DataFile(
                type='NCDF',
                download_datetime=timezone.now(),
                generated_datetime=modified_datetime,
                model_date=model_date,
                file=local_filename,
            )
            datafile.save()

            new_file_ids.append(datafile.id)

        return new_file_ids

    @staticmethod
    @shared_task(name='pl_download.get_latest_wave_watch_files')
    def get_latest_wave_watch_files():

        #list of the new file ids created in this function
        new_file_ids = []

        #directory of where files will be saved at
        destination_directory = os.path.join(settings.MEDIA_ROOT, settings.WAVE_WATCH_DIR)

        #file names might need to be created dynamically in the future if ftp site changes
        file_name = "outer.nc"
        #static_file_names = ["shelf1.nc", "shelf2.nc", "shelf3.nc"]

        #Connect to FTP site to get the file modification data
        ftp = FTP('cil-www.oce.orst.edu')
        ftp.login()

        #retrieve the ftp modified datetime format
        ftp_dtm = ftp.sendcmd('MDTM' + " /pub/outgoing/ww3data/" + file_name)

        #convert ftp datetime format to a string datetime
        modified_datetime = datetime.strptime(ftp_dtm[4:], "%Y%m%d%H%M%S").strftime("%Y-%m-%d")

        # check if we've downloaded it before: does DataFile contain an entry whose model_date matches this one
        # that is also a WaveWatch file?
        matches_old_file = DataFile.objects.filter(
           model_date=modified_datetime,
           file__startswith="OuterGrid"
        )
        if not matches_old_file:
            #Create File Name and Download actual File into media folder
            url = urljoin(settings.WAVE_WATCH_URL, file_name)
            local_filename = "{0}_{1}_{2}.nc".format("OuterGrid", modified_datetime, uuid4())
            urllib.urlretrieve(url=url, filename=os.path.join(destination_directory, local_filename))

            #Save the File name into the Database
            datafile = DataFile(
                type='WAVE',
                download_datetime=timezone.now(),
                generated_datetime=modified_datetime,
                model_date = modified_datetime,
                file=local_filename,
            )

            datafile.save()

            new_file_ids.append(datafile.id)

            #quit ftp connection cause we accessed all the data we need
            ftp.quit()
            return new_file_ids

        #Must have already downloaded this file
        else:
            ftp.quit()
            return []

    @classmethod
    def get_next_few_days_files_from_db(cls):

        next_few_days_of_files = DataFile.objects.filter(
            #set back to -timedelta 2 hrs
            model_date__gte=(timezone.now()-timedelta(days=2)).date(),
            model_date__lte=(timezone.now()+timedelta(days=4)).date()
        )

        #Select the most recent within each model date and type (ie wave or SST)
        and_the_newest_for_each_model_date = next_few_days_of_files.values('model_date', 'type').annotate(newest_generation_time=Max('generated_datetime'))

        # if we expected a lot of new files, this would be bad (we're making a Q object for each file we want, basically)
        q_objects = []
        for filedata in and_the_newest_for_each_model_date:
            new_q = Q(type=filedata.get('type'), model_date=filedata.get('model_date'),
                      generated_datetime=filedata.get('newest_generation_time'))
            q_objects.append(new_q)

        # assumes you're not redownloading the same file for the same model and generation dates.
        actual_datafile_objects = DataFile.objects.filter(reduce(OR, q_objects))

        return actual_datafile_objects

    @classmethod
    def is_new_file_to_download(cls):
        three_days_ago = timezone.now().date()-timedelta(days=3)
        today = timezone.now().date()

        #Look back at the past 3 days of datafiles
        recent_netcdf_files = DataFile.objects.filter(model_date__range=[three_days_ago, today])

        # empty lists return false
        if not recent_netcdf_files:
            return True

        local_file_modified_datetime = recent_netcdf_files.latest('generated_datetime').generated_datetime

        tree = get_ingria_xml_tree()
        tags = tree.iter(XML_NAMESPACE + 'dataset')

        for elem in tags:
            if not elem.get('name').startswith('ocean_his'):
                continue
            server_file_modified_datetime = extract_modified_datetime_from_xml(elem)
            if server_file_modified_datetime <= local_file_modified_datetime:
                return False

        return True

    @classmethod
    def is_new_wave_watch_file_to_download(cls):
        three_days_ago = timezone.now().date()-timedelta(days=3)
        today = timezone.now().date()

        #Look back at the past 3 days of datafiles
        recent_netcdf_files = WaveWatchDataFile.objects.filter(generated_datetime__range=[three_days_ago, today])

        # empty lists return false
        if not recent_netcdf_files:
            return True

        local_file_modified_datetime = recent_netcdf_files.latest('generated_datetime').generated_datetime

        tree = get_ingria_xml_tree()
        tags = tree.iter(XML_NAMESPACE + 'dataset')

        for elem in tags:
            if not elem.get('name').startswith('ocean_his'):
                continue
            server_file_modified_datetime = extract_modified_datetime_from_xml(elem)
            if server_file_modified_datetime <= local_file_modified_datetime:
                return False

        return True

    @classmethod
    def delete_old_files(cls):
        how_old_to_keep = timezone.datetime.now()-timedelta(days=HOW_LONG_TO_KEEP_FILES)

        # NETCDF files
        #The old files are those whose model_date is less than the time after which we want to keep (ie going back 10 days)
        old_netcdf_files = DataFile.objects.filter(model_date__lte=how_old_to_keep)

        # Delete the file items from the database, and the actual image files.
        for filename in old_netcdf_files:

            DataFile.delete(filename) # Custom delete method for DataFiles: this deletes the actual files from disk too


        #TILES folder holds directories only. There are no Tile items in the database so we don't have to delete those.
        how_old_to_keep = timezone.datetime.now()-timedelta(days=HOW_LONG_TO_KEEP_FILES)

        directory=os.path.join('/opt/sharkeyes/media/tiles/')

        # Reference here:  http://stackoverflow.com/questions/2237909/delete-old-directories-in-python
        for r,d,f in os.walk(directory):
            for direc in d:
                timestamp = timezone.datetime.fromtimestamp(os.path.getmtime(os.path.join(r,direc)))

                if how_old_to_keep > timestamp:
                    try:
                        shutil.rmtree(os.path.join(r,direc))
                    except Exception,e:
                        print e
                        pass

        return True


#not using this right now. Better to just use DataFile for new model types rather than making a new class.
class WaveWatchDataFile(models.Model):
    DATA_FILE_TYPES = (
        ('NCDF', "NetCDF"),
    )
    type = models.CharField(max_length=10, choices=DATA_FILE_TYPES, default='NCDF')
    download_datetime = models.DateTimeField()
    generated_datetime = models.DateTimeField()
    file = models.FileField(upload_to=settings.NETCDF_STORAGE_DIR, null=True)



class DataFile(models.Model):
    DATA_FILE_TYPES = (
        ('NCDF', "NetCDF", "Wave"),
    )
    type = models.CharField(max_length=10, choices=DATA_FILE_TYPES, default='NCDF')
    download_datetime = models.DateTimeField()
    generated_datetime = models.DateTimeField()
    model_date = models.DateField()
    file = models.FileField(upload_to=settings.NETCDF_STORAGE_DIR, null=True)

    #Custom delete method which will also delete the DataFile's image file from the disk
    def delete(self,*args,**kwargs):
        #Seems to be a Django bug (?) which gives the wrong path for self.file.path. This is a workaround.
        pathName = os.path.join(
        settings.MEDIA_ROOT  + settings.NETCDF_STORAGE_DIR + "/" + self.file.name)

        if os.path.isfile(pathName):
            #Delete the physical file from disk
            os.remove(pathName)

        #Delete the model instance
        super(DataFile, self).delete(*args,**kwargs)

