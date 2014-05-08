from django.shortcuts import render
from pl_plot.models import *

def home(request):
    context = {'overlays': Overlay.objects.all()}
    return render(request, 'index.html', context)
