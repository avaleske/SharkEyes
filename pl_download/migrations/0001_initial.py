# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataFile'
        db.create_table(u'pl_download_datafile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='NCDF', max_length=10)),
            ('download_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
        ))
        db.send_create_signal(u'pl_download', ['DataFile'])


    def backwards(self, orm):
        # Deleting model 'DataFile'
        db.delete_table(u'pl_download_datafile')


    models = {
        u'pl_download.datafile': {
            'Meta': {'object_name': 'DataFile'},
            'download_date': ('django.db.models.fields.DateTimeField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'NCDF'", 'max_length': '10'})
        }
    }

    complete_apps = ['pl_download']