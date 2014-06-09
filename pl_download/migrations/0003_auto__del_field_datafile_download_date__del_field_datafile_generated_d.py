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

    models = {
        u'pl_download.datafile': {
            'Meta': {'object_name': 'DataFile'},
            'download_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'generated_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_date': ('django.db.models.fields.DateField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'NCDF'", 'max_length': '10'})
        }
    }

    complete_apps = ['pl_download']