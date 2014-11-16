#!/bin/sh
/opt/sharkeyes/env_sharkeyes/bin/python -u /vagrant/manage.py celery worker --loglevel=INFO