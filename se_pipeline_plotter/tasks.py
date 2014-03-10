from __future__ import absolute_import
from celery import shared_task
import time


@shared_task
def add(x, y):
    time.sleep(10)
    return x + y