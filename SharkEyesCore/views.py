from django.shortcuts import render
from pl_plot.models import OverlayManager

def home(request):
    context = {'overlays': OverlayManager.get_next_few_days_of_tiled_overlays()}
    return render(request, 'index.html', context)
