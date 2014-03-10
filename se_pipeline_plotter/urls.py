__author__ = 'avaleske'
from django.conf.urls import patterns, url
from se_pipeline_plotter import views

urlpatterns = patterns('',
                       url(r'^test/', views.add, name='add')
)