#!/bin/sh
/home/vagrant/virtualenvs/sharkeyes/bin/python -u /vagrant/manage.py celery worker --loglevel=INFO