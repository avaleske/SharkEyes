source /home/vagrant/virtualenvs/sharkeyes/bin/activate

pypath="/home/vagrant/virtualenvs/sharkeyes/bin/python"

$pypath -u /vagrant/manage.py syncdb
$pypath -u /vagrant/manage.py migrate djcelery
$pypath -u /vagrant/manage.py migrate pl_plot
$pypath -u /vagrant/manage.py migrate pl_download

sudo rabbitmq-server -detatched
