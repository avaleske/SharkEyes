from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files import File
import os
from django.conf import settings
from celery import group
from datetime import datetime
from django.utils.timezone import utc
from django.utils import timezone
from celery import shared_task
from pl_plot import plot_functions
from pl_plot.plotter import Plotter
from pl_download.models import DataFile


class OverlayManager(models.Manager):
    @staticmethod
    def get_all_base_definition_ids():
        return OverlayDefinition.objects.values_list('id').filter(is_base=True)

    @classmethod
    def make_all_base_plots(cls):
        task_list = [make_plot.subtask(args=od_id, link=save_overlay.s()) for od_id in cls.get_all_base_definition_ids()]
        job = group(task_list)
        results = job.apply_async()  # this might just be returning results from the first task in each chain
        return [result[0] for result in results.get()]


@shared_task(name='pl_plot.make_plot')
def make_plot(overlay_definition_id):
    # this just grabs the most recent file. Should the file be tied to the overlay model?
    datafile = DataFile.objects.latest('model_date')
    plotter = Plotter(datafile.file.name)
    overlay_definition = OverlayDefinition.objects.get(pk=overlay_definition_id)
    filename = plotter.make_plot(getattr(plot_functions, overlay_definition.function_name))
    return filename, overlay_definition_id

@shared_task(name='pl_plot.save_overlay')
def save_overlay((filename, od_id)):
    overlay = Overlay(
        file=os.path.join(settings.UNCHOPPED_STORAGE_DIR, filename),
        date_created=timezone.now(),
        definition_id=od_id,
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
    date_created = models.DateTimeField()
    file = models.ImageField(upload_to=settings.UNCHOPPED_STORAGE_DIR, null=True)
    tile_dir = models.CharField(max_length=240, null=True)