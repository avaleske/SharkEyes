from django.shortcuts import render
from django.http import HttpResponse
from pl_plot.tasks import add
from pl_plot.models import OverlayManager


def testfunc(request):
    result = add.delay(3, 4)
    print(result.get())
    return HttpResponse("the result was {0}".format(str(result.get())))


def testplot(request):
    OverlayManager.make_all_base_plots()
    return HttpResponse("hope that worked...")