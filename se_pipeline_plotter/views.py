from django.shortcuts import render
from django.http import HttpResponse
from se_pipeline_plotter.tasks import add
from tasks import test_temp_plot


def testfunc(request):
    result = add.delay(3, 4)
    print(result.get())
    return HttpResponse("the result was {0}".format(str(result.get())))


def testplot(request):
    result = test_temp_plot.delay()
    return HttpResponse(result.get())