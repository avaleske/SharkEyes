# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Rename 'name' field to 'full_name'
        db.rename_column('pl_download_datafile', 'download_date', 'download_datetime')
        db.rename_column('pl_download_datafile', 'generated_date', 'generated_datetime')

    def backwards(self, orm):
        # Rename 'full_name' field to 'name'
        db.rename_column('pl_download_datafile', 'download_datetime', 'download_date')
        db.rename_column('pl_download_datafile', 'generated_datetime', 'generated_date')

    complete_apps = ['pl_download']