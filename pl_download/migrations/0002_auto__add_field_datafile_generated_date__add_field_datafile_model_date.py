# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DataFile.generated_date'
        db.add_column(u'pl_download_datafile', 'generated_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 31, 0, 0)),
                      keep_default=False)

        # Adding field 'DataFile.model_date'
        db.add_column(u'pl_download_datafile', 'model_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 3, 31, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DataFile.generated_date'
        db.delete_column(u'pl_download_datafile', 'generated_date')

        # Deleting field 'DataFile.model_date'
        db.delete_column(u'pl_download_datafile', 'model_date')


    models = {
        u'pl_download.datafile': {
            'Meta': {'object_name': 'DataFile'},
            'download_date': ('django.db.models.fields.DateTimeField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'generated_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_date': ('django.db.models.fields.DateField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'NCDF'", 'max_length': '10'})
        }
    }

    complete_apps = ['pl_download']