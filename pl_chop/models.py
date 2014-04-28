from django.db import models
from pl_plot.models import OverlayManager, Overlay
from celery import group
from pl_chop.tasks import chop_overlay
import time


class TileManager():
    def __init__(self):
        None

    @staticmethod
    def tile_most_recent_overlays():
        overlay_ids_to_tile = OverlayManager.get_newest_untiled_overlay_ids()
        if len(overlay_ids_to_tile) != 0:
            task_list = [chop_overlay.s(o_id) for o_id in overlay_ids_to_tile]
            job = group(task_list)
            results = job.apply_async()  # this might just be returning results from the first task in each chain
            return results
        return []