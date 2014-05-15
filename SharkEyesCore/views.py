from django.shortcuts import render
from pl_plot.models import OverlayManager, OverlayDefinition
from dateutil import tz

def home(request):
    overlays_view_data = OverlayManager.get_next_few_days_of_tiled_overlays()

    datetimes = [ i.applies_at_datetime.astimezone(tz.tzlocal()).strftime('%A, %I %p') for i in overlays_view_data ]

    # a complete hack! it just divides a list of all of the times for all the overlays by the number
    # of defs to get a singular list of overlay times
    num_defs = len(OverlayDefinition.objects.all())
    list_of_times = datetimes[:len(datetimes)/num_defs]

    context = {'overlays': overlays_view_data, 'defs': OverlayDefinition.objects.all(), 'times':list_of_times }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')
