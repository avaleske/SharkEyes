#!/bin/sh
source /home/vagrant/virtualenvs/sharkeyes/bin/activate

pypath="/home/vagrant/virtualenvs/sharkeyes/bin/python"

${pypath} -u /vagrant/manage.py syncdb
${pypath} -u /vagrant/manage.py migrate djcelery
${pypath} -u /vagrant/manage.py migrate pl_plot
${pypath} -u /vagrant/manage.py migrate pl_download

sudo rabbitmq-server -detatched &
sleep 3
echo "Waiting 3 seconds for rabbitmq to start"

${pypath} -u /vagrant/manage.py celery worker --loglevel=INFO &
sleep 3
echo "Waiting 3 seconds for celery to start"

sudo sh ./runserver.sh