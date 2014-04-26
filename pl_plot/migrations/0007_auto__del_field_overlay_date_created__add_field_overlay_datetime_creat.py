# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Rename 'name' field to 'full_name'
        db.rename_column('pl_plot_overlay', 'date_created', 'datetime_created')

    def backwards(self, orm):
        # Rename 'full_name' field to 'name'
        db.rename_column('app_foo', 'datetime_created', 'date_created')

    complete_apps = ['pl_plot']