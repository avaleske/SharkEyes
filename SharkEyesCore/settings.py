"""
Django settings for SharkEyesCore project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
from __future__ import absolute_import

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w^_kzwp&gk9z9%(8_6sgcc4lvyw=_4x8v1!c$kmvblnwu6ad1g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'celery',
    'djcelery',
    'south',
    'pl_download',
    'pl_plot',
    'pl_chop',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'SharkEyesCore.urls'

WSGI_APPLICATION = 'SharkEyesCore.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sharkeyes',
        'USER': 'sharkeyes',
        'PASSWORD': 'secureme',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = BASE_DIR + '/templates/'

STATIC_URL = '/synced_dir/'
STATIC_ROOT = '/vagrant/synced_dir/'

STATICFILES_DIRS = (
    BASE_DIR + '/synced_dir/',
     '/var/www/synced_dir/',
)

# other files
#definitely a temporary option
NETCDF_STORAGE_DIR = "netcdf"
UNCHOPPED_STORAGE_DIR = "unchopped"
VRT_STORAGE_DIR = "vrt_files"
TILE_STORAGE_DIR = "tiles"
KEY_STORAGE_DIR = "keys"

BASE_NETCDF_URL = "http://ingria.coas.oregonstate.edu/opendap/ACTZ/"

MEDIA_ROOT = "/home/vagrant/media_root/"

# For celery
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_VHOST = "sharkeyes"
BROKER_USER = "sharkeyes"
BROKER_PASSWORD = "secureme"

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
