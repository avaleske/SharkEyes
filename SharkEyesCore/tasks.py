from __future__ import absolute_import
from celery import shared_task
from celery import chain
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
        return False

    # chain the pipeline steps together. si() creates the task signature immutably. Otherwise, the result of one task
    # gets passed to the next one in the chain, which isn't what we want.
    job = chain(
        DataFileManager.fetch_new_files_task.si(),
        OverlayManager.get_task_for_base_plots_for_next_few_days().si(),
        spacer_task.si(),                                       # Need the spacer so all the plots finish before tiling
        TileManager.get_task_to_tile_next_few_days_of_untiled_overlays().si()
    )
    job.get()
    return True


@shared_task(name='sharkeyescore.spacer')
def spacer_task():
    pass