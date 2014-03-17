__author__ = 'avaleske'
from django.http import HttpResponse


def home(request):
    return HttpResponse("Welcome to the home page. We need to have this part work...")