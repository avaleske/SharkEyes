from django.shortcuts import render
from pl_plot.models import OverlayManager, OverlayDefinition
from dateutil import tz
import json
from django.db import connection
from django.db import IntegrityError, transaction

def home(request):
    overlays_view_data = OverlayManager.get_next_few_days_of_tiled_overlays()

    datetimes = [ i.applies_at_datetime.astimezone(tz.tzlocal()).strftime('%D, %I %p') for i in overlays_view_data ]

    # a complete hack! it just divides a list of all of the times for all the overlays by the number
    # of defs to get a singular list of overlay times
    num_defs = len(OverlayDefinition.objects.filter(is_base=True))
    list_of_times = datetimes[:len(datetimes)/num_defs]

    context = {'overlays': overlays_view_data, 'defs': OverlayDefinition.objects.filter(is_base=True), 'times':list_of_times }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

def save_feedback(request):
    #Access feedback data to be saved into the database
    feedback_title = json.loads(request.body)["title"]
    feedback_comment = json.loads(request.body)["comment"]

    try:
        #Establish DB Connection
        cursor = connection.cursor()
        #Execute SQL Query
        cursor.execute("""INSERT INTO SharkEyesCore_feedbackhistory (feedback_title, feedback_comments) VALUES (%s, %s);""", (feedback_title, feedback_comment))
        #Nothing needs to be returned
    except IntegrityError as e:
        print "Error Message: "
        print e.message
    return render(request, 'index.html')