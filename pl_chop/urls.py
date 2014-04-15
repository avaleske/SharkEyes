from django.conf.urls import patterns, url
from pl_chop import views

urlpatterns = patterns('',
        url(r'^testchop/', views.test_chop, name='testchop'),
)