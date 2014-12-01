from django.shortcuts import render
from django.http import HttpResponse
from pl_plot.models import Overlay
from pl_chop.tasks import chop_overlay
from pl_chop.models import TileManager


def test_chop(request):
    #Validate User Permissions
    if request.user.is_anonymous():
        return HttpResponse("You do not have admin permissions to this site. Please contact your page administrator.")
    else:
        results = TileManager.tile_next_few_days_of_untiled_overlays()
        if results is None:
            return HttpResponse("Nothing to tile")
        else:
            return HttpResponse(results.get().__str__())