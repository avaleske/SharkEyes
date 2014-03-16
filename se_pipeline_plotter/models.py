from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from celery import group
from datetime import datetime
from se_pipeline_plotter.tasks import make_plot

print('models!')


class OverlayManager(models.Manager):
    @staticmethod
    def get_all_base_definition_ids():
        return [oid[0] for oid in OverlayDefinition.objects.values_list('id').filter(is_base=True)]

    @classmethod
    def make_all_base_plots(cls):
        task_list = [make_plot.s(oid) for oid in cls.get_all_base_definition_ids()]
        job = group(task_list)
        results = job.apply_async()
        for result in results.get():
            overlay = Overlay()
            overlay.file = result[0]
            overlay.date_created = datetime.now()
            overlay.definition_id = result[1]
            overlay.save()



class OverlayDefinition(models.Model):
    OVERLAY_TYPES = (
        ('V', 'Vector'),
        ('FC', 'Filled Contour'),
    )
    type = models.CharField(max_length=4, choices=OVERLAY_TYPES)
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