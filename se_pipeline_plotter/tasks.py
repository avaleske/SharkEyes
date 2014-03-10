from __future__ import absolute_import
from celery import shared_task
import time
from se_pipeline_plotter.plotter import Plotter
import se_pipeline_plotter.plot_methods as pm

FILE_NAME = "ocean_his_3322_04-Feb-2014.nc"


@shared_task(name='tasks.add')
def add(x, y):
    time.sleep(10)
    return x + y


@shared_task(name='tasks.test_temp_plot')
def test_temp_plot():
    plotter = Plotter()
    data_file = plotter.load_file(FILE_NAME)
    plotter.make_plot(data_file, pm.temp_method)
    return "completed plotting. check sync_dir/unchopped/"