from __future__ import absolute_import
from celery import shared_task, chain, subtask, group
import time
from pl_download.models import DataFileManager
from pl_plot.models import OverlayManager
from pl_chop.models import TileManager
from pl_chop.tasks import tile_overlay
from pl_chop.tasks import tile_wave_watch_overlay


@shared_task(name='sharkeyescore.add')
def add(a, b):
    #time.sleep(5)
    return a + b


@shared_task(name='sharkeyescore.pipeline')
def do_pipeline():
    print "TASKS: before deleting files"

    DataFileManager.delete_old_files()
    print "TASKS: after deleting Datafiles"
    OverlayManager.delete_old_files()
    print "TASKS: after deleting Overlays"

    wave_watch_files = DataFileManager.get_latest_wave_watch_files()
    print "TASKS: after getting wave files"

    other_files = DataFileManager.fetch_new_files()   # not calling as a task so it runs inline
    print "TASKS: after getting sst/currents files"

    # If no new files were returned, don't plot or tile anything.
    if not wave_watch_files and not other_files:
        return None

    # get the list of plotting tasks based on the files we just downloaded.
    plot_task_list = OverlayManager.get_tasks_for_base_plots_for_next_few_days()

    list_of_chains = []

    for pt in plot_task_list:

        if pt.args[0] != 4 and pt.args[0] != 6:
            # chaining passes the result of first function to second function
            list_of_chains.append(chain(pt, tile_overlay.s()))

        else:
            # TODO this wave tiler should be fine for both Direction and Height
            #Use the Wavewatch tiler for Wavewatch files
            list_of_chains.append(chain(pt, tile_wave_watch_overlay.s()))

    job = group(item for item in list_of_chains)
    print "jobs:"
    for each in job:
        print each
     #and run the group.
    result = job.apply_async()
    return result



@shared_task(name='sharkeyescore.spacer_task')
def spacer_task(args=None):
    if args is not None:
        return args
    return None
