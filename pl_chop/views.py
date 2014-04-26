from django.shortcuts import render
from django.http import HttpResponse
from pl_plot.models import Overlay
from pl_chop.tasks import chop_overlay


def test_chop(request):
    overlay = Overlay.objects.latest('datetime_created')
    result = chop_overlay.delay(overlay.id)
    return HttpResponse(result.get())