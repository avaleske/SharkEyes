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

    DataFileManager.delete_old_files()
    OverlayManager.delete_old_files()

    # wave watch file takes care of its own check to see if there are new WaveWatchfiles
    DataFileManager.get_latest_wave_watch_files()
    #if not DataFileManager.is_new_file_to_download():
        #return None
    
    DataFileManager.fetch_new_files()   # not calling as a task so it runs inline

    # get the list of plotting tasks based on the files we just downloaded.
    #This should know about WaveWatch files
    #TODO: this won't be run unless there is a new SST/currents file!
    plot_task_list = OverlayManager.get_tasks_for_base_plots_for_next_few_days()
    print "Plot tasks:"
    for each in plot_task_list:
        #if each.args[0] == 4: #it's a wavewatch file so use the wavewatch tiler
        #elif each.args[0] == 5: #it's a Wind file so use the Wind tiler
        #else:
        print each


    #tile_overlay is independent of WaveWatch vs SST: it will do both
    # create a task chain of (plot, tile) for each plot, and group them
    #job = group(chain(pt, tile_overlay.s()) for pt in plot_task_list if pt.args[0] != 4)
    list_of_chains = []
    for pt in plot_task_list:
        if pt.args[0] != 4:
            list_of_chains.append(chain(pt, tile_overlay.s()))
        else:
            #Tile a wavewatch overlay
            list_of_chains.append(chain(pt, tile_wave_watch_overlay.s()))

    job = group(item for item in list_of_chains)
    print "job:"
    for each in job:
        print each
    # and run the group.
    result = job.apply_async()
    return result


@shared_task(name='sharkeyescore.spacer_task')
def spacer_task(args=None):
    if args is not None:
        return args
    return None
