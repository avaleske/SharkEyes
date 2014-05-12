from django.db import models
from pl_plot.models import OverlayManager, Overlay
from celery import group
from pl_chop.tasks import chop_overlay
import time


class TileManager():
    def __init__(self):
        None

    @classmethod
    def tile_most_recent_overlays(cls):
        overlay_ids_to_tile = OverlayManager.get_newest_untiled_overlay_ids()
        return cls.tile_overlays_from_ids(overlay_ids_to_tile)

    @classmethod
    def tile_next_few_days_of_untiled_overlays(cls):
        overlay_ids_to_tile = OverlayManager.get_next_few_days_of_untiled_overlay_ids()
        return cls.tile_overlays_from_ids(overlay_ids_to_tile)

    @staticmethod
    def tile_overlays_from_ids(overlay_ids):
        if len(overlay_ids) != 0:
            task_list = [chop_overlay.s(o_id) for o_id in overlay_ids]
            job = group(task_list)
            results = job.apply_async()  # this might just be returning results from the first task in each chain
            return results
        return []