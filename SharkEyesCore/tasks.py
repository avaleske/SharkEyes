from __future__ import absolute_import
from celery import shared_task, chain, subtask, group
import time
from pl_download.models import DataFileManager
from pl_plot.models import OverlayManager
from pl_chop.models import TileManager


@shared_task(name='sharkeyescore.add')
def add(a, b):
    #time.sleep(5)
    return a + b

@shared_task(name='sharkeyescore.pipeline')
def do_pipeline():
    if not DataFileManager.is_new_file_to_download():
     #   return None
        pass

    DataFileManager.fetch_new_files() #not calling as a task so it runs inline

    plot_group = OverlayManager.get_task_for_base_plots_for_next_few_days()

    job = chain(plot_group.s(), spacer_task.si(), TileManager.get_task_to_tile_next_few_days_of_untiled_overlays().si())

    result = job.apply_async()
    return result


@shared_task(name='sharkeyescore.spacer_task')
def spacer_task(arg=None):
    return sum(arg)