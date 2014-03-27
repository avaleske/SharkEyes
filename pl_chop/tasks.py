from celery import shared_task
from pl_plot.models import Overlay
from pl_chop import gdal2tiles
from uuid import uuid4
import os
from django.conf import settings


@shared_task(name='pl_chop.chop_overlay')
def chop_overlay(overlay_id):
    overlay = Overlay.objects.get(pk=overlay_id)
    print("in task")
    image = overlay.file
    print("has image")
    width = image.width
    print("has width")
    height = image.height
    tile_dir = "tiles-{0}".format(uuid4())

    '''
    ended up running this manually, which seems to have worked
    gdal_translate -of VRT -a_srs EPSG:4326 -gcp 0 0 -129 47.499  -gcp 2100 0 -123.726 47.499 -gcp 2100 3840 -123.726 40.5833 /home/vagrant/media_root/unchopped/sst_function-56a0e322-c9b9-4213-a938-9d9dd24ad82e.png sst_function-56a0e322-c9b9-4213-a938-9d9dd24ad82e.vrt

    '''

    translate_cmd = ("gdal_translate -of VRT -a_srs EPSG:4326 -gcp 0 0 -129 47.499 "
                     "-gcp {0} 0 -123.726 47.499 -gcp {0} {1} -123.726 40.5833 {2} {3}.vrt").format(
            str(width), str(height), image.name, os.path.splitext(image.name))

    os.system(translate_cmd)

    #todo Yeah. I know. Shut up.
    tile_gen_cmd = ("/home/vagrant/virtualenvs/sharkeyes/python gdal2tiles.py "
                    "--profile=mercator -z 4-10 {0}.vrt {1}").format(image.name, tile_dir)
    os.system(tile_gen_cmd)

    overlay.tile_dir = tile_dir
    overlay.save()
    return tile_dir