# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'OverlayDefinition.is_base'
        db.add_column(u'pl_plot_overlaydefinition', 'is_base',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Overlay.file'
        db.alter_column(u'pl_plot_overlay', 'file', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True))

    def backwards(self, orm):
        # Deleting field 'OverlayDefinition.is_base'
        db.delete_column(u'pl_plot_overlaydefinition', 'is_base')


        # Changing field 'Overlay.file'
        db.alter_column(u'pl_plot_overlay', 'file', self.gf('django.db.models.fields.files.ImageField')(default=False, max_length=100))

    models = {
        u'pl_plot.overlay': {
            'Meta': {'object_name': 'Overlay'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pl_plot.OverlayDefinition']"}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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