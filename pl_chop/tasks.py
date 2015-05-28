from celery import shared_task
from pl_plot.models import Overlay
from pl_plot.models import Wave_Watch_Overlay
from pl_chop import gdal2tiles
from uuid import uuid4
import os
import subprocess
from gdal2tiles import GDAL2Tiles
from django.conf import settings



#tile one overlay (SST, currents or wavewatch), based on the ID of that overlay
@shared_task(name='pl_chop.tile_overlay')
def tile_overlay(overlay_id):

    # todo if we get a list of overlay_ids (which happens if there are multiple zoom levels) then recursively call
    # itself with the ids in the list. It should only be two or three things. Once there's a better way for
    # handling multiple zoom levels, this can likely go away.
    if isinstance(overlay_id, list):
        if len(overlay_id)>1:
            tile_dirs = []
            for oid in overlay_id:
                tile_dirs.extend(tile_overlay(oid))
            return tile_dirs

    #the id's in the database progresses upwards from 1. If overlays are deleted, the new
    # overlays start numbering where the old ones
    #left  off. Ie if we delete items 1-100, the new overlays will start numbering at 101.

    overlay = Overlay.objects.get(pk=overlay_id)
    image = overlay.file
    width = image.width
    height = image.height

    # get zoom level
    if overlay.zoom_levels is not None and len(overlay.zoom_levels) > 0:
        zoom_levels = overlay.zoom_levels
    else:
        zoom_levels ='2-10' #default zoom levels

    print zoom_levels

    full_tile_dir = os.path.join(settings.MEDIA_ROOT, settings.TILE_STORAGE_DIR, overlay.tile_dir)
    vrt_path = os.path.join(settings.MEDIA_ROOT, settings.VRT_STORAGE_DIR, "{0}.vrt".format(uuid4()))

    #These co-ordinates are only OK for the SST/currents model
    translate_cmd = ("/usr/local/bin/gdal_translate -of VRT -a_srs EPSG:4326 -gcp 0 0 -129 47.499 "
                     "-gcp {0} 0 -123.726 47.499 -gcp {0} {1} -123.726 40.5833 {2} {3}").format(
            str(width), str(height), image.path, vrt_path)

    # Team 1 says: calling this with shell=True is insecure if we had input from the user,
    # but all our input is trusted, so we're good.
    status = subprocess.call(translate_cmd, shell=True)
    if status != 0:
        raise Exception("gdal_translate failed")

    # Team 1 says: see if we don't need gdal_translate for this to work...
    params = ['--profile=mercator', '-z', zoom_levels, '-w', 'none', vrt_path, full_tile_dir]
    tile_generator = GDAL2Tiles(params)
    tile_generator.process()

    overlay.is_tiled = True     # this could be a overlay.update(tile_dir=tile_dir) in django 1.7
    overlay.save()
    return overlay.tile_dir

@shared_task(name='pl_chop.tile_wave_watch_overlay')
def tile_wave_watch_overlay(overlay_id):

   # todo if we get a list of overlay_ids (which happens if there are multiple zoom levels) then recursively call
    # itself with the ids in the list. It should only be two or three things. Once there's a better way for
    # handling multiple zoom levels, this can likely go away.
    if isinstance(overlay_id, list):
        if len(overlay_id)>1:
            tile_dirs = []
            for oid in overlay_id:
                tile_dirs.extend(tile_wave_watch_overlay(oid))
            return tile_dirs

    #the id's in the database progresses upwards from 1. If overlays are deleted, the new
    # overlays start numbering where the old ones
    #left  off. Ie if we delete items 1-100, the new overlays will start numbering at 101.

    overlay = Overlay.objects.get(pk=overlay_id)
    image = overlay.file
    width = image.width
    height = image.height

    # get zoom level
    if overlay.zoom_levels is not None and len(overlay.zoom_levels) > 0:
        zoom_levels = overlay.zoom_levels
    else:
        zoom_levels ='2-10' #default zoom levels

    print zoom_levels

    full_tile_dir = os.path.join(settings.MEDIA_ROOT, settings.TILE_STORAGE_DIR, overlay.tile_dir)
    vrt_path = os.path.join(settings.MEDIA_ROOT, settings.VRT_STORAGE_DIR, "{0}.vrt".format(uuid4()))

    #wavewatch co-ords are 41.458 to 47.508N and from 127.8 to 123.758W (see Fig. 1).
    translate_cmd = ("/usr/local/bin/gdal_translate -of VRT -a_srs EPSG:4326 -gcp 0 0 -127.8 47.508 "
                    "-gcp {0} 0 -123.69 47.508 -gcp {0} {1} -123.69 41.458 {2} {3}").format(
            str(width), str(height), image.path, vrt_path)

    # Team 1 says: calling this with shell=True is insecure if we had input from the user,
    # but all our input is trusted, so we're good.
    status = subprocess.call(translate_cmd, shell=True)
    if status != 0:
        raise Exception("gdal_translate failed")

    # Team 1 says: see if we don't need gdal_translate for this to work...
    params = ['--profile=mercator', '-z', zoom_levels, '-w', 'none', vrt_path, full_tile_dir]
    tile_generator = GDAL2Tiles(params)
    tile_generator.process()

    overlay.is_tiled = True     # this could be a overlay.update(tile_dir=tile_dir) in django 1.7
    overlay.save()
    return overlay.tile_dir