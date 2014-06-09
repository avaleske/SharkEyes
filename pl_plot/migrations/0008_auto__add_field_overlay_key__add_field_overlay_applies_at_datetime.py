# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Overlay.key'
        db.add_column(u'pl_plot_overlay', 'key',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True),
                      keep_default=False)

        # Adding field 'Overlay.applies_at_datetime'
        db.add_column(u'pl_plot_overlay', 'applies_at_datetime',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Overlay.key'
        db.delete_column(u'pl_plot_overlay', 'key')

        # Deleting field 'Overlay.applies_at_datetime'
        db.delete_column(u'pl_plot_overlay', 'applies_at_datetime')


    models = {
        u'pl_plot.overlay': {
            'Meta': {'object_name': 'Overlay'},
            'applies_at_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'datetime_created': ('django.db.models.fields.DateTimeField', [], {}),
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pl_plot.OverlayDefinition']"}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'tile_dir': ('django.db.models.fields.CharField', [], {'max_length': '240', 'null': 'True'})
        },
        u'pl_plot.overlaydefinition': {
            'Meta': {'object_name': 'OverlayDefinition'},
            'display_name_long': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '240'}),
            'display_name_short': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'function_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_base': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'pl_plot.parameters': {
            'Meta': {'object_name': 'Parameters'},
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pl_plot.OverlayDefinition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '240'})
        }
    }

    complete_apps = ['pl_plot']