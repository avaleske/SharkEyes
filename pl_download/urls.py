__author__ = 'avaleske'
from django.conf.urls import patterns, url
from pl_download import views

urlpatterns = patterns('',
        url(r'^testfetch/', views.test_fetch, name='testfetch'),
)