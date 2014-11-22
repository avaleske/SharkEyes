__author__ = 'avaleske'
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
import os
import matplotlib
matplotlib.use('Agg')   # set matplotlib backend to not use xwindow as early as possible in app startup

def setup_dirs():
    # make sure we have a place to put stuff.
    for directory in [
                        settings.NETCDF_STORAGE_DIR,
                        settings.UNCHOPPED_STORAGE_DIR,
                        settings.VRT_STORAGE_DIR,
                        settings.TILE_STORAGE_DIR,
                        settings.KEY_STORAGE_DIR]:
        dest = os.path.join(settings.MEDIA_ROOT, directory)
        if not os.path.exists(dest):
            os.makedirs(dest)

def run():
    setup_dirs()
