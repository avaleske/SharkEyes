__author__ = 'avaleske'
from django.conf.urls import patterns, url
from se_pipeline_plotter import views

urlpatterns = patterns('',
        url(r'^add/', views.testfunc, name='add'),
        url(r'^testplot/', views.testplot, name='testplot'),
)