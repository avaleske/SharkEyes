from django.shortcuts import render
from django.http import HttpResponse
from pl_plot.models import Overlay
from pl_chop.tasks import chop_overlay
from pl_chop.models import TileManager


def test_chop(request):
    result = TileManager.tile_next_few_days_of_untiled_overlays()
    return HttpResponse(result.get())