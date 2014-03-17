from __future__ import absolute_import
from celery import shared_task
import time
from pl_plot import plot_functions
from pl_plot.plotter import Plotter




@shared_task(name='tasks.add')
def add(x, y):
    time.sleep(10)
    return x + y



