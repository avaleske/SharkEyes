# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'FeedbackQuestionaire.ss_temperature_accuracy'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'ss_temperature_accuracy', self.gf('django.db.models.fields.CharField')(max_length=4))

        # Changing field 'FeedbackQuestionaire.usage_device'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'usage_device', self.gf('django.db.models.fields.CharField')(max_length=4))

        # Changing field 'FeedbackQuestionaire.usage_location'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'usage_location', self.gf('django.db.models.fields.CharField')(max_length=4))

        # Changing field 'FeedbackQuestionaire.usage_frequency'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'usage_frequency', self.gf('django.db.models.fields.CharField')(max_length=4))

        # Changing field 'FeedbackQuestionaire.ss_currents_accuracy'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'ss_currents_accuracy', self.gf('django.db.models.fields.CharField')(max_length=4))

    def backwards(self, orm):

        # Changing field 'FeedbackQuestionaire.ss_temperature_accuracy'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'ss_temperature_accuracy', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'FeedbackQuestionaire.usage_device'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'usage_device', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'FeedbackQuestionaire.usage_location'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'usage_location', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'FeedbackQuestionaire.usage_frequency'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'usage_frequency', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'FeedbackQuestionaire.ss_currents_accuracy'
        db.alter_column(u'SharkEyesCore_feedbackquestionaire', 'ss_currents_accuracy', self.gf('django.db.models.fields.CharField')(max_length=255))

    models = {
        u'SharkEyesCore.feedbackhistory': {
            'Meta': {'object_name': 'FeedbackHistory'},
            'feedback_comments': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'feedback_title': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'SharkEyesCore.feedbackquestionaire': {
            'Meta': {'object_name': 'FeedbackQuestionaire'},
            'consult': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'general_comments': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_comments': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'ss_currents_accuracy': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'ss_temperature_accuracy': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'usage_comparison': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'usage_device': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'usage_frequency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'usage_likes': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'usage_location': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'usage_model_suggestion': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'usage_suggestion': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        }
    }

    complete_apps = ['SharkEyesCore']