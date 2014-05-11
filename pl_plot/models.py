from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files import File
import os
from django.conf import settings
from celery import group
from datetime import datetime, time, tzinfo
from django.utils.timezone import utc
from django.utils import timezone
from celery import shared_task
from pl_plot import plot_functions
from pl_plot.plotter import Plotter
from pl_download.models import DataFile
from django.db.models.aggregates import Max


class OverlayManager(models.Manager):
    @staticmethod
    def get_all_base_definition_ids():
        return OverlayDefinition.objects.values_list('id', flat=True).filter(is_base=True)

    @staticmethod
    def get_newest_untiled_overlay_ids():
        # assuming newer overlays have higher primary keys. Seems reasonable.
        overlay_definitions = OverlayDefinition.objects.annotate(newest_overlay_id=Max('overlay__id'))
        newest_overlays = Overlay.objects.filter(id__in=[od.newest_overlay_id for od in overlay_definitions])
        return newest_overlays.filter(tile_dir__isnull=True).values_list('id', flat=True)

    @classmethod
    def make_all_base_plots(cls):
        task_list = [make_plot.s(od_id) for od_id in cls.get_all_base_definition_ids()]
        job = group(task_list)
        results = job.apply_async()  # this might just be returning results from the first task in each chain
        return results.get()

    @classmethod
    def get_current_overlays(cls):
        # 'current' is defined as the closest overlay to now, forward or backwards.
        None

    @classmethod
    def get_next_overlays(cls):
        # 'next' is defined as the overlay after the closest overlay to now.
        None


@shared_task(name='pl_plot.make_plot')
def make_plot(overlay_definition_id):
    # this just grabs the most recent file. Should the file be tied to the overlay model?
    datafile = DataFile.objects.latest('model_date')
    plotter = Plotter(datafile.file.name)
    overlay_definition = OverlayDefinition.objects.get(pk=overlay_definition_id)
    plot_filename, key_filename = plotter.make_plot(getattr(plot_functions, overlay_definition.function_name))

    overlay = Overlay(
        file=os.path.join(settings.UNCHOPPED_STORAGE_DIR, plot_filename),
        key=os.path.join(settings.KEY_STORAGE_DIR, key_filename),
        created_datetime=timezone.now(),
        definition_id=overlay_definition_id,
        # we're grabbing the one for 4 am for now. Assuming utc...
        applies_at_datetime=timezone.make_aware(datetime.combine(datafile.model_date, time(4)), timezone.utc),
    )
    overlay.save()
    return overlay.id


class OverlayDefinition(models.Model):
    OVERLAY_TYPES = (
        ('V', 'Vector'),
        ('FC', 'Filled Contour'),
    )
    type = models.CharField(max_length=4, choices=OVERLAY_TYPES)
        #it might turn out that these don't have to be unique
    display_name_long = models.CharField(max_length=240, unique=True)
    display_name_short = models.CharField(max_length=64)
    function_name = models.CharField(max_length=64, unique=True)
    is_base = models.BooleanField(default=False)


# this acts as a dictionary for the definition, so we can provide additional parameters.
class Parameters(models.Model):
    definition = models.ForeignKey(OverlayDefinition)
    key = models.CharField(max_length=240)
    value = models.CharField(max_length=240)


class Overlay(models.Model):
    definition = models.ForeignKey(OverlayDefinition)
    created_datetime = models.DateTimeField()
    file = models.ImageField(upload_to=settings.UNCHOPPED_STORAGE_DIR, null=True)
    tile_dir = models.CharField(max_length=240, null=True)
    key = models.ImageField(upload_to=settings.KEY_STORAGE_DIR, null=True)
    applies_at_datetime = models.DateTimeField(null=False)