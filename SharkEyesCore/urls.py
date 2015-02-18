from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'SharkEyesCore.views.home', name='home'),
    url(r'^about.html', 'SharkEyesCore.views.about', name='about'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pl_plot/', include('pl_plot.urls')),
    url(r'^pl_download/', include('pl_download.urls')),
    url(r'^pl_chop/', include('pl_chop.urls')),
    url(r'^SharkEyesCore', 'SharkEyesCore.views.save_feedback')
)

if settings.DEBUG == True:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
