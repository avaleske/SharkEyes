from __future__ import absolute_import
from celery import shared_task, chain, subtask, group
import time
from pl_download.models import DataFileManager
from pl_plot.models import OverlayManager
from pl_chop.models import TileManager
from pl_chop.tasks import tile_overlay


@shared_task(name='sharkeyescore.add')
def add(a, b):
    #time.sleep(5)
    return a + b

@shared_task(name='sharkeyescore.pipeline')
def do_pipeline():
    if not DataFileManager.is_new_file_to_download():
        return None
    DataFileManager.delete_old_files()
    OverlayManager.delete_old_files()
    
    DataFileManager.fetch_new_files()   # not calling as a task so it runs inline


    # get the list of plotting tasks based on the files we just downloaded.
    plot_task_list = OverlayManager.get_tasks_for_base_plots_for_next_few_days()

    # create a task chain of (plot, tile) for each plot, and group them
    job = group(chain(pt, tile_overlay.s()) for pt in plot_task_list)

    # and run the group.
    result = job.apply_async()
    return result


@shared_task(name='sharkeyescore.spacer_task')
def spacer_task(args=None):
    if args is not None:
        return args
    return None
