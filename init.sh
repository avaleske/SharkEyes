#!/bin/sh
source /home/vagrant/virtualenvs/sharkeyes/bin/activate

pypath="/opt/sharkeyes/env_sharkeyes/bin/python"

${pypath} -u /opt/sharkeyes/src/manage.py syncdb
${pypath} -u /opt/sharkeyes/src/manage.py migrate djcelery
${pypath} -u /opt/sharkeyes/src/manage.py migrate pl_chop
${pypath} -u /opt/sharkeyes/src/manage.py migrate pl_plot
${pypath} -u /opt/sharkeyes/src/manage.py migrate pl_download

sudo rabbitmq-server -detatched &
sleep 3
echo "Waiting 3 seconds for rabbitmq to start"

${pypath} -u /opt/sharkeyes/src/manage.py celery worker --loglevel=INFO &
sleep 3
echo "Waiting 3 seconds for celery to start"

sudo sh ./runserver.sh