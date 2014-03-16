# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'OverlayDefinition', fields ['display_name_long']
        db.create_unique(u'se_pipeline_plotter_overlaydefinition', ['display_name_long'])

        # Adding unique constraint on 'OverlayDefinition', fields ['function_name']
        db.create_unique(u'se_pipeline_plotter_overlaydefinition', ['function_name'])


    def backwards(self, orm):
        # Removing unique constraint on 'OverlayDefinition', fields ['function_name']
        db.delete_unique(u'se_pipeline_plotter_overlaydefinition', ['function_name'])

        # Removing unique constraint on 'OverlayDefinition', fields ['display_name_long']
        db.delete_unique(u'se_pipeline_plotter_overlaydefinition', ['display_name_long'])


    models = {
        u'se_pipeline_plotter.overlay': {
            'Meta': {'object_name': 'Overlay'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['se_pipeline_plotter.OverlayDefinition']"}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'se_pipeline_plotter.overlaydefinition': {
            'Meta': {'object_name': 'OverlayDefinition'},
            'display_name_long': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '240'}),
            'display_name_short': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'function_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'se_pipeline_plotter.parameters': {
            'Meta': {'object_name': 'Parameters'},
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['se_pipeline_plotter.OverlayDefinition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '240'})
        }
    }

    complete_apps = ['se_pipeline_plotter']