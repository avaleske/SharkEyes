# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Overlay'
        db.create_table(u'se_pipeline_plotter_overlay', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'se_pipeline_plotter', ['Overlay'])


    def backwards(self, orm):
        # Deleting model 'Overlay'
        db.delete_table(u'se_pipeline_plotter_overlay')


    models = {
        u'se_pipeline_plotter.overlay': {
            'Meta': {'object_name': 'Overlay'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        }
    }

    complete_apps = ['se_pipeline_plotter']