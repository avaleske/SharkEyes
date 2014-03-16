from __future__ import absolute_import
from celery import shared_task
import time
from se_pipeline_plotter import plot_functions
from se_pipeline_plotter.plotter import Plotter
from se_pipeline_plotter.models import OverlayDefinition

FILE_NAME = "ocean_his_3322_04-Feb-2014.nc"


@shared_task(name='tasks.add')
def add(x, y):
    time.sleep(10)
    return x + y


@shared_task(name='se_pipeline_plotter.make_plot')
def make_plot(overlay_definition_id):
    print("in task")
    plotter = Plotter(FILE_NAME)
    overlay_definition = OverlayDefinition.objects.get(pk=overlay_definition_id)
    filename = plotter.make_plot(getattr(plot_functions, overlay_definition.function_name))
    return filename
