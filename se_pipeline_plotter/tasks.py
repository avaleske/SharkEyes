from __future__ import absolute_import
from celery import shared_task
import time
from se_pipeline_plotter.plotter import Plotter
from se_pipeline_plotter import plot_functions
from se_pipeline_plotter import models

FILE_NAME = "ocean_his_3322_04-Feb-2014.nc"


@shared_task(name='tasks.add')
def add(x, y):
    time.sleep(10)
    return x + y


@shared_task(name='tasks.test_temp_plot')
def test_temp_plot():
    plotter = Plotter()
    data_file = plotter.load_file(FILE_NAME)
    plotter.make_plot(data_file, plot_functions.sst_function())
    return "completed plotting. check sync_dir/unchopped/"

@shared_task(name='se_pipeline_plotter.make_plot')
def make_plot(overlay_id):
    overlay = models.Overlay.objects.get(pk=overlay_id)
    plotter = Plotter()
    data_file = plotter.load_file(FILE_NAME)
    plotter.make_plot(data_file, getattr(plot_functions, overlay.definition.id.__str__()))
    return "completed plotting. check sync_dir/unchopped/"
