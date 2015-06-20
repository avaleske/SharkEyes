from django.shortcuts import render
from pl_plot.models import OverlayManager, OverlayDefinition
from dateutil import tz
import json
from django.db import connection
from django.db import IntegrityError, transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


#This is where we associate the Javascript variables (overlays, defs etc) with the Django objects from the database.
def home(request):
    overlays_view_data = OverlayManager.get_next_few_days_of_tiled_overlays().exclude(definition_id=5)
    #Wind overlay is different from the main overlay due to the time intervals
    wind_overlays_view_data = overlays_view_data.filter(definition_id=5)

    datetimes = [ i.applies_at_datetime.astimezone(tz.tzlocal()).strftime('%D, %I %p') for i in overlays_view_data ]
    print datetimes
    winddatetimes = [ i.applies_at_datetime.astimezone(tz.tzlocal()).strftime('%D, %I %p') for i in wind_overlays_view_data ]
    print winddatetimes

    # a complete hack! it just divides a list of all of the times for all the overlays by the number
    # of defs to get a singular list of overlay times
    num_defs = len(OverlayDefinition.objects.filter(is_base=True).exclude(display_name_short="Wind"))
    print num_defs
    num_wind_defs = len(OverlayDefinition.objects.filter(is_base=True).exclude(display_name_short="SST").exclude(display_name_short="Currents"))
    list_of_times = datetimes[:len(datetimes)/num_defs]
    print list_of_times
    list_of_wind_times = winddatetimes[:len(winddatetimes)/num_wind_defs]
    print list_of_wind_times

    context = {'overlays': overlays_view_data, 'defs': OverlayDefinition.objects.filter(is_base=True).exclude(id=4), 'times':list_of_times, 'windoverlays': wind_overlays_view_data, 'winddefs': OverlayDefinition.objects.filter(id=5), 'windtimes':list_of_wind_times}

    return render(request, 'index.html', context)


def about(request):
    return render(request, 'about.html')

@csrf_exempt
def survey(request):
    return render(request, 'survey.html')

@csrf_exempt
def save_survey(request):
    usage_location = json.loads(request.body)["usage_location"]
    usage_frequency = json.loads(request.body)["usage_frequency"]
    usage_device = json.loads(request.body)["usage_device"]
    ss_temperature_accuracy = json.loads(request.body)["sst_accuracy"]
    ss_currents_accuracy = json.loads(request.body)["currents_accuracy"]
    wave_accuracy = json.loads(request.body)["wave_accuracy"]
    wind_accuracy = json.loads(request.body)["wind_accuracy"]
    usage_comparison = json.loads(request.body)["usage_comparison"]
    usage_likes = json.loads(request.body)["usage_likes"]
    usage_suggestion = json.loads(request.body)["usage_suggestion"]
    usage_model_suggestion = json.loads(request.body)["usage_model_suggestion"]
    general_comment = json.loads(request.body)["usage_comments"]

    try:
        #Establish DB Connection
        cursor = connection.cursor()
        #Execute SQL Query
        cursor.execute("""INSERT INTO SharkEyesCore_feedbackquestionaire(usage_location, usage_frequency, usage_device,usage_comment, ss_temperature_accuracy, ss_currents_accuracy, wave_accuracy,  wind_accuracy, usage_comparison,usage_likes, usage_suggestion, usage_model_suggestion ) VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s);""",(usage_location, usage_frequency, usage_device, general_comment, ss_temperature_accuracy, ss_currents_accuracy,wave_accuracy, wind_accuracy, usage_comparison, usage_likes, usage_suggestion, usage_model_suggestion))
        #Nothing needs to be returned
    except IntegrityError as e:
        print "Error Message: "
        print e.message

    return render(request, 'survey.html')
@csrf_exempt
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