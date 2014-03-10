from django.shortcuts import render
from django.http import HttpResponse
from tasks import add


def testfunc(request):
    result = add.apply_async(args=[3, 4], kwargs={})
    print(result.get())
    return HttpResponse("the result was " + result.get())