from __future__ import absolute_import
from django.conf import settings
from celery import shared_task
import time

@shared_task(name='sharkeyescore.add')
def add(a, b):
    time.sleep(5)
    return a + b