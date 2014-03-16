__author__ = 'avaleske'
import datetime
from se_pipeline_plotter.models import Overlay, OverlayManager
from se_pipeline_plotter import tasks

print("base")

#todo move all this stuff to overlay manager?
class PlotManager():
    def make_all_base_plots(self):
        # todo find a way to not reload the netcdf file for every plot maybe?
        # plotter = Plotter(FILE_NAME)

        #todo this is synchronous, which sucks. make it async with celery groups
        for overlay_definition in OverlayManager.get_all_base_definitions():
            print("looking at id " + str(overlay_definition.id))
            result = tasks.make_plot.delay(overlay_definition.id)
            filename = result.get()
            overlay = Overlay(definition=overlay_definition)
            overlay.date_created = datetime.datetime.now()
            overlay.file = filename
            overlay.save()