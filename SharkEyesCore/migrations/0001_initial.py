# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeedbackHistory'
        db.create_table(u'SharkEyesCore_feedbackhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('feedback_comments', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'SharkEyesCore', ['FeedbackHistory'])


    def backwards(self, orm):
        # Deleting model 'FeedbackHistory'
        db.delete_table(u'SharkEyesCore_feedbackhistory')


    models = {
        u'SharkEyesCore.feedbackhistory': {
            'Meta': {'object_name': 'FeedbackHistory'},
            'feedback_comments': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'feedback_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['SharkEyesCore']