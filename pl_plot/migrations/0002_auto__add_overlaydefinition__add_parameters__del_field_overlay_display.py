# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OverlayDefinition'
        db.create_table(u'pl_plot_overlaydefinition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('function_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'pl_plot', ['OverlayDefinition'])

        # Adding model 'Parameters'
        db.create_table(u'pl_plot_parameters', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('definition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pl_plot.OverlayDefinition'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=240)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=240)),
        ))
        db.send_create_signal(u'pl_plot', ['Parameters'])

        # Deleting field 'Overlay.display_name'
        db.delete_column(u'pl_plot_overlay', 'display_name')

        # Deleting field 'Overlay.type'
        db.delete_column(u'pl_plot_overlay', 'type')

        # Adding field 'Overlay.definition'
        db.add_column(u'pl_plot_overlay', 'definition',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pl_plot.OverlayDefinition']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'OverlayDefinition'
        db.delete_table(u'pl_plot_overlaydefinition')

        # Deleting model 'Parameters'
        db.delete_table(u'pl_plot_parameters')

        # Adding field 'Overlay.display_name'
        db.add_column(u'pl_plot_overlay', 'display_name',
                      self.gf('django.db.models.fields.CharField')(default='default_name', max_length=64),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Overlay.type'
        raise RuntimeError("Cannot reverse this migration. 'Overlay.type' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Overlay.type'
        db.add_column(u'pl_plot_overlay', 'type',
                      self.gf('django.db.models.fields.CharField')(max_length=4),
                      keep_default=False)

        # Deleting field 'Overlay.definition'
        db.delete_column(u'pl_plot_overlay', 'definition_id')


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
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
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