# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'OverlayDefinition.display_name'
        db.delete_column(u'pl_plot_overlaydefinition', 'display_name')

        # Adding field 'OverlayDefinition.display_name_long'
        db.add_column(u'pl_plot_overlaydefinition', 'display_name_long',
                      self.gf('django.db.models.fields.CharField')(default='long name', max_length=240),
                      keep_default=False)

        # Adding field 'OverlayDefinition.display_name_short'
        db.add_column(u'pl_plot_overlaydefinition', 'display_name_short',
                      self.gf('django.db.models.fields.CharField')(default='short name', max_length=64),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'OverlayDefinition.display_name'
        raise RuntimeError("Cannot reverse this migration. 'OverlayDefinition.display_name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'OverlayDefinition.display_name'
        db.add_column(u'pl_plot_overlaydefinition', 'display_name',
                      self.gf('django.db.models.fields.CharField')(max_length=64),
                      keep_default=False)

        # Deleting field 'OverlayDefinition.display_name_long'
        db.delete_column(u'pl_plot_overlaydefinition', 'display_name_long')

        # Deleting field 'OverlayDefinition.display_name_short'
        db.delete_column(u'pl_plot_overlaydefinition', 'display_name_short')


    models = {
        u'pl_plot.overlay': {
            'Meta': {'object_name': 'Overlay'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pl_plot.OverlayDefinition']"}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pl_plot.overlaydefinition': {
            'Meta': {'object_name': 'OverlayDefinition'},
            'display_name_long': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'display_name_short': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'function_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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