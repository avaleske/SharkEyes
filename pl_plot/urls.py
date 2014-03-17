__author__ = 'avaleske'
from django.conf.urls import patterns, url
from pl_plot import views

urlpatterns = patterns('',
        url(r'^add/', views.testfunc, name='add'),
        url(r'^testplot/', views.testplot, name='testplot'),
)