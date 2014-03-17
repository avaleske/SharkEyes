from __future__ import absolute_import
from celery import shared_task
import time
from se_pipeline_plotter import plot_functions
from se_pipeline_plotter.plotter import Plotter




@shared_task(name='tasks.add')
def add(x, y):
    time.sleep(10)
    return x + y



