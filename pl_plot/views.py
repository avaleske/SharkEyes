from django.shortcuts import render
from django.http import HttpResponse
from pl_plot.models import OverlayManager

def testplot(request):
    group_results = OverlayManager.make_all_base_plots_for_next_few_days()
    name_list = [result.get() for result in group_results]
    return HttpResponse("plotted files " + name_list.__str__())