from django.shortcuts import render
from pl_plot.models import OverlayManager, OverlayDefinition
from dateutil import tz

#This is where we associate the Javascript variables (overlays, defs etc) with the Django objects from the database.
def home(request):

    overlays_view_data = OverlayManager.get_next_few_days_of_tiled_overlays()

    datetimes = [ i.applies_at_datetime.astimezone(tz.tzlocal()).strftime('%D, %I %p') for i in overlays_view_data ]
    unrendereddatetimes = [ i.applies_at_datetime.strftime('%D, %I %p') for i in overlays_view_data ]
    print "datetimes are",
    for e in datetimes:
        print e

    print "unrendered datetimes are",
    for e in unrendereddatetimes:
        print e

    # Team 1 says: a complete hack! it just divides a list of all of the times for all the overlays by the number
    # of defs to get a singular list of overlay times
    num_defs = len(OverlayDefinition.objects.filter(is_base=True))
    print "numdefs = ", num_defs
    list_of_times = datetimes[:len(datetimes)/num_defs]
   #need to make all three (sst, currents, and wavewatch in order for there to be THREE datetimes)
    print "list of times", list_of_times

    context = {'overlays': overlays_view_data, 'defs': OverlayDefinition.objects.filter(is_base=True), 'times':list_of_times }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')
