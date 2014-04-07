from django.db import models
from django.conf import settings
from celery import shared_task
from urlparse import urljoin
from django.utils import timezone
import urllib
import os
from uuid import uuid4
from django.conf import settings
from urlparse import urljoin
import urllib2
from defusedxml import ElementTree
from datetime import datetime
from dateutil import parser, tz

CATALOG_XML_NAME = "catalog.xml"
XML_NAMESPACE = "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}"


def check_for_new_file():
    xml_url = urljoin(settings.BASE_NETCDF_URL, CATALOG_XML_NAME)
    last_generated_time = DataFile.objects.latest('generated_date').generated_date

    catalog_xml = urllib2.urlopen(xml_url)
    tree = ElementTree.parse(catalog_xml)
    tags = tree.iter(XML_NAMESPACE + 'dataset')

    for elem in tags:
        if not elem.get('name').startswith('ocean_his'):
            continue
        mod_date_string = elem.find(XML_NAMESPACE + 'date').text
        naive_date = parser.parse(mod_date_string)  # the date in the xml file follows iso standards, so we're gold.
        mod_date = timezone.make_aware(naive_date, timezone.utc)
        if mod_date <= last_generated_time:
            return False


@shared_task(name='pl_download.fetch_new_file')
def fetch_new_file():


    server_filename = "ocean_his_3362_16-Mar-2014.nc"
    local_filename = "{0}x-{1}.nc".format(timezone.now().date().strftime('%m-%d-%Y'), uuid4())



    url = urljoin(settings.BASE_NETCDF_URL, server_filename)
    urllib.urlretrieve(url=url, filename=os.path.join(dest, local_filename))

    datafile = DataFile(
        type='NCDF',
        download_date=timezone.now(),
        file=local_filename,
    )
    datafile.save()
    return datafile.file.name


class DataFile(models.Model):
    DATA_FILE_TYPES = (
        ('NCDF', "NetCDF"),
    )
    type = models.CharField(max_length=10, choices=DATA_FILE_TYPES, default='NCDF')
    download_date = models.DateTimeField()
    generated_date = models.DateTimeField()
    model_date = models.DateField()
    file = models.FileField(upload_to=settings.NETCDF_STORAGE_DIR, null=True)
