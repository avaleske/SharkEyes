from django.db import models
from pl_plot.models import OverlayManager, Overlay
from celery import group, shared_task
from pl_chop.tasks import tile_overlay
import numpy
import time


#Automated tiling: an Overlay is created (one image that covers the whole screen), then it is Tiled/Chopped or broken up
#into small pieces that Google Maps can knit together into a zoomable image.
class TileManager():
    def __init__(self):
        None

    @classmethod
    def tile_next_few_days_of_overlays(cls):
        job = cls.get_task_to_tile_next_few_days_of_untiled_overlays()
        result = job.apply_async()
        return result

    # These just return task signatures that can be executed whenever.
    @classmethod
    def get_task_to_tile_newest_untiled_overlays(cls):
        overlay_ids_to_tile = OverlayManager.get_newest_untiled_overlay_ids()
        return cls.get_tiling_task_by_ids(overlay_ids_to_tile)

    @classmethod
    def get_task_to_tile_next_few_days_of_untiled_overlays(cls):
        overlay_ids_to_tile = OverlayManager.get_next_few_days_of_untiled_overlay_ids()
        return cls.get_tiling_task_by_ids(overlay_ids_to_tile)

    @classmethod
    def get_tiling_task_by_ids(cls, overlay_ids):
        if len(overlay_ids) != 0:
            flattened = numpy.hstack(overlay_ids)
            job = group((tile_overlay.s(o_id, immutable=True) for o_id in flattened))
            return job
        return None


