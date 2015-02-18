from django.shortcuts import render
from django.http import HttpResponse
from pl_plot.models import OverlayManager
from django.http import Http404

def testplot(request):
    #Validate User Permissions
    if request.user.is_anonymous():
        raise Http404("You do not have admin permissions to this site. Please contact your page administrator.")
    else:
        group_results = OverlayManager.make_all_base_plots_for_next_few_days()
        name_list = [result.get() for result in group_results]
        return HttpResponse("plotted files " + name_list.__str__())