from django.shortcuts import render
from django.http import HttpResponse
from pl_plot.tasks import add
from pl_plot.models import OverlayManager

def testplot(request):
    name_list = OverlayManager.make_all_base_plots()
    return HttpResponse("plotted files " + name_list.__str__())