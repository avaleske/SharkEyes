"""
WSGI config for SharkEyesCore project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
import site

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SharkEyesCore.settings")
os.environ["CELERY_LOADER"] = "django"
os.environ["MPLCONFIGDIR"] = "/opt/.mpl_tmp"

site.addsitedir('/opt/sharkyes/env_sharkeyes/lib/python2.7/site-packages')
sys.path.append('/opt/sharkeyes/src')
sys.path.append('/opt/sharkeyes/src/SharkEyesCore')

activate_env = os.path.expanduser('/opt/sharkeyes/env_sharkeyes/bin/activate_this.py')
execfile(activate_env, dict(__file__=activate_env))

import SharkEyesCore.startup as startup
startup.run()

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

'''
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
'''