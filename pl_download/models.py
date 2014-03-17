from django.db import models
from django.conf import settings
from celery import shared_task
from urlparse import urljoin
from os import path
from django.utils import timezone
import urllib
from uuid import uuid4

BASE_NETCDF_URL = "http://ingria.coas.oregonstate.edu/opendap/ACTZ/"

@shared_task(name='pl_download.fetch_new_file')
def fetch_new_file():
    #todo this is currently really really dumb. Like, it doesn't even check to see if it
    # even got the file for today already, or if it got the newest one, or anything.

    server_filename = "ocean_his_3362_16-Mar-2014.nc"
    local_filename = "{0}-{1}.nc".format(timezone.now().date().strftime('%m-%d-%Y'), uuid4())

    url = urljoin(BASE_NETCDF_URL, server_filename)
    urllib.urlretrieve(url=url, filename=path.join(
        settings.MEDIA_ROOT,
        settings.NETCDF_STORAGE_DIR,
        local_filename)
    )

    datafile = DataFile(
        type='NCDF',
        download_date=timezone.now(),
        file=local_filename,
    )
    datafile.save()
    return datafile.id


class DataFile(models.Model):
    DATA_FILE_TYPES = (
        ('NCDF', "NetCDF"),
    )
    type = models.CharField(max_length=10, choices=DATA_FILE_TYPES, default='NCDF')
    download_date = models.DateTimeField()
    file = models.FileField(upload_to=settings.NETCDF_STORAGE_DIR, null=True)
    #todo we should add a date-generated field that we pull from the catalog xml
