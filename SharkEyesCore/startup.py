__author__ = 'avaleske'
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
import os

def setup_dirs():
    # make sure we have a place to put stuff.
    for directory in [settings.NETCDF_STORAGE_DIR,
                      settings.UNCHOPPED_STORAGE_DIR,
                      settings.VRT_STORAGE_DIR,
                      settings.TILE_STORAGE_DIR]:
        dest = os.path.join(settings.MEDIA_ROOT, directory)
        if not os.path.exists(dest):
            os.makedirs(dest)


def autoload(submodules):
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        for submodule in submodules:
            try:
                import_module("{}.{}".format(app, submodule))
            except:
                if module_has_submodule(mod, submodule):
                    raise


def run():
    setup_dirs()
    autoload(['base'])
