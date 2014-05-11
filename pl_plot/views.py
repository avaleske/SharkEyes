from django.shortcuts import render
from django.http import HttpResponse
from pl_plot.models import OverlayManager

def testplot(request):
    results = OverlayManager.make_all_base_plots()
    name_list = results.get()
    return HttpResponse("plotted files " + name_list.__str__())