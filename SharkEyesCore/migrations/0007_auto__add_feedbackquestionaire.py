# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeedbackQuestionaire'
        db.create_table(u'SharkEyesCore_feedbackquestionaire', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usage_location', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('usage_frequency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('usage_device', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('general_comments', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('ss_temperature_accuracy', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('ss_currents_accuracy', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('wave_accuracy', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('usage_comparison', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('usage_likes', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('usage_suggestion', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('usage_model_suggestion', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal(u'SharkEyesCore', ['FeedbackQuestionaire'])


    def backwards(self, orm):
        # Deleting model 'FeedbackQuestionaire'
        db.delete_table(u'SharkEyesCore_feedbackquestionaire')


    models = {
        u'SharkEyesCore.feedbackhistory': {
            'Meta': {'object_name': 'FeedbackHistory'},
            'feedback_comments': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'feedback_title': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'SharkEyesCore.feedbackquestionaire': {
            'Meta': {'object_name': 'FeedbackQuestionaire'},
            'general_comments': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ss_currents_accuracy': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'ss_temperature_accuracy': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'usage_comparison': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'usage_device': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'usage_frequency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'usage_likes': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'usage_location': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'usage_model_suggestion': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'usage_suggestion': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'wave_accuracy': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        }
    }

    complete_apps = ['SharkEyesCore']