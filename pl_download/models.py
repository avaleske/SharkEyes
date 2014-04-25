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
from datetime import datetime, timedelta
from dateutil import parser, tz

CATALOG_XML_NAME = "catalog.xml"
XML_NAMESPACE = "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}"


def get_ingria_xml_tree():
    # todo: need to handle if the xml file isn't available
    xml_url = urljoin(settings.BASE_NETCDF_URL, CATALOG_XML_NAME)
    catalog_xml = urllib2.urlopen(xml_url)
    tree = ElementTree.parse(catalog_xml)
    return tree


def extract_modified_date_from_xml(elem):
    modified_date_string = elem.find(XML_NAMESPACE + 'date').text
    naive_date = parser.parse(modified_date_string)  # the date in the xml file follows iso standards, so we're gold.
    modified_date = timezone.make_aware(naive_date, timezone.utc)
    return modified_date


def is_new_published_netcdf_file():
    last_generated_time = DataFile.objects.filter(model_date__lte=timezone.now().date()).latest('generated_date').generated_date

    tree = get_ingria_xml_tree()
    tags = tree.iter(XML_NAMESPACE + 'dataset')

    for elem in tags:
        if not elem.get('name').startswith('ocean_his'):
            continue
        modified_date = extract_modified_date_from_xml(elem)
        if modified_date <= last_generated_time:
            return False
        else:
            return True


@shared_task(name='pl_download.fetch_new_files')
# grabs file for today only, for now.
def fetch_new_files():
    if not is_new_published_netcdf_file():
        return False

    # download new file for today and tomorrow
    days_to_retrieve = [timezone.now().date(), timezone.now().date()+timedelta(days=1)]
    files_to_retrieve = []
    tree = get_ingria_xml_tree()    # yes, we just did this to see if there's a new file. refactor later.
    tags = tree.iter(XML_NAMESPACE + 'dataset')

    for elem in tags:
        server_filename = elem.get('name')
        if not server_filename.startswith('ocean_his'):
            continue
        date_string_from_filename = server_filename.split('_')[-1]
        model_date = datetime.strptime(date_string_from_filename, "%d-%b-%Y.nc").date()   # this could fail, need error handling badly
        modified_date = extract_modified_date_from_xml(elem)

        for day_to_retrieve in days_to_retrieve:
            if model_date - day_to_retrieve == timedelta(days=0):
                files_to_retrieve.append((server_filename, model_date, modified_date))

    destination_directory = os.path.join(settings.MEDIA_ROOT, settings.NETCDF_STORAGE_DIR)

    for server_filename, model_date, modified_date in files_to_retrieve:
        url = urljoin(settings.BASE_NETCDF_URL, server_filename)
        local_filename = "{0}-{1}.nc".format(model_date, uuid4())
        urllib.urlretrieve(url=url, filename=os.path.join(destination_directory, local_filename))

        datafile = DataFile(
            type='NCDF',
            download_date=timezone.now(),
            generated_date = modified_date,
            model_date = model_date,
            file=local_filename,
        )
        datafile.save()

    return True


class DataFile(models.Model):
    DATA_FILE_TYPES = (
        ('NCDF', "NetCDF"),
    )
    type = models.CharField(max_length=10, choices=DATA_FILE_TYPES, default='NCDF')
    download_date = models.DateTimeField()
    generated_date = models.DateTimeField()
    model_date = models.DateField()
    file = models.FileField(upload_to=settings.NETCDF_STORAGE_DIR, null=True)
