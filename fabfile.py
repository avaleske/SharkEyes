#!/usr/bin/env python

# If running this on a critical system that shouldn't reboot, comment out the reboot() command in setup_group()
# The script will fail with a permissions error at that point, just run it again from the start and it will work.

# Before running this, make sure you've filled out settings_local.py.
# If you're running this against a production server, then make sure you've also set up git ssh keys with github.

# Finally, all the functions that'd you'd expect to be should be idempotent, save for configure_apache(), which
# will overwrite /etc/httpd/sites-available/sharkeyes with whatever's in the config/apache folder of the project.

from fabric.api import run, env, sudo, local, cd, settings, prefix, reboot
from fabric.contrib.console import confirm, prompt
from fabric.contrib.files import exists
from fabric.context_managers import shell_env
from getpass import getpass

# we'd use requirements.txt, but some of these have install time dependencies because they suck
python_packages = ['numpy==1.8',
                   'nose==1.1',
                   'scipy==0.10',
                   'matplotlib==1.1',
                   'pandas==0.8',
                   'MySQL-python==1.2.3c1',
                   'django==1.6.2',
                   'pillow==2.3.0',
                   'pytz==2013.9',
                   'celery==3.1.9',
                   'django-celery==3.1.9',
                   'south==0.8.4',
                   'defusedxml==0.4.1',
                   'pygdal==1.10.1.0',
                   ]

# these aren't used everywhere yet...
PROJECT_ROOT = '/opt/sharkeyes'
SRC_ROOT = '/opt/sharkeyes/src'

def vagrant():
    """Allow fabric to manage a Vagrant VM/LXC container"""
    env.user = 'vagrant'
    v = dict(map(lambda l: l.strip().split(), local('vagrant ssh-config', capture=True).split('\n')))
    # Build a valid host entry
    env.hosts = ["%s:%s" % (v['HostName'],v['Port'])]
    # Use Vagrant SSH key
    if v['IdentityFile'][0] == '"':
        env.key_filename = v['IdentityFile'][1:-1]
    else:
        env.key_filename = v['IdentityFile']
    env.branch = 'develop'

def staging():
    env.user = 'azureuser'
    hostname = 'fishable.cloudapp.net'
    port = 22
    env.hosts = env.hosts = ["%s:%s" % (hostname,port)]
    env.branch = 'staging'

def install_prereqs():
    #handle selinux
    with settings(warn_only=True):
        if run('rpm -qa |grep selinux').return_code == 0:
            if 'Enforcing' in run('/usr/sbin/getenforce'):
                with settings(warn_only=False):
                    sudo('/usr/sbin/setsebool httpd_tmp_exec on')

    make_dir('/opt/installers')
    # repos
    sudo('yum -y install epel-release')
    with settings(warn_only=True):
        with cd('/opt/installers'):
            if run('rpm -q elgis-release-6-6_0.noarch').return_code != 0:
                sudo('wget http://elgis.argeo.org/repos/6/elgis-release-6-6_0.noarch.rpm')
                sudo('rpm -Uvh elgis-release-6-6_0.noarch.rpm')

    # sudo('yum -y update')                               # careful here if not on a new machine
    sudo('yum -y groupinstall "Development tools"')
    sudo('yum -y install vim emacs man wget zlib-devel bzip2-devel openssl-devel ncurses-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel')


def install_python27():
    if not exists('/usr/bin/python2.7'):
        with cd('/opt/installers/'):
            sudo('wget https://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz')
            sudo('tar -xvzf Python-2.7.3.tgz')
        with cd('/opt/installers/Python-2.7.3/'):
            sudo('./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"')
            sudo('make && make altinstall')
        with cd('/usr/local/lib/python2.7/config/'):
            sudo('ln -s ../../libpython2.7.so.1.0')     # linking so other stuff knows where to find Python
            sudo('ln -s ../../libpython2.7.so')
        sudo('ln -s /usr/local/bin/python2.7 /usr/bin/')    # and adding another link so it's easy to use the right one later
    sudo('yum -y install python-pip python-devel')          # todo is it a problem that this is python 2.6.6 devel?
    sudo('pip install --upgrade pip')
    sudo('pip install virtualenv')
    sudo('pip install virtualenvwrapper')


def install_apache():
    sudo('yum -y install httpd')
    sudo('yum -y install httpd-devel')
    make_dir('/etc/httpd/sites-available')
    make_dir('/etc/httpd/sites-enabled')


def install_mysql():
    if is_centos_7():
        with settings(warn_only=True):
            if run('rpm -q mysql-community-release-el7-5.noarch').return_code != 0:
                sudo('rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el7-5.noarch.rpm')
    sudo('yum -y install mysql mysql-devel')
    #sudo('yum -y install MySQL-python') # moved to virtualenv
    sudo('yum -y install mysql-server')


def setup_group():
    current_user = run('id -u -n')
    with settings(warn_only=True):
        if run('grep sharkeyes /etc/group').return_code != 0:
            sudo('groupadd sharkeyes')
    sudo('usermod -a -G sharkeyes apache')
    sudo('usermod -a -G sharkeyes mysql')
    sudo('usermod -a -G sharkeyes ' + current_user)
    #sudo('exec sudo su -l $USER')
    if 'sharkeyes' not in run('id'):
        if env.user == 'vagrant':
            local('vagrant reload') # if we're in vagrant, a normal restart doesn't reconnect things it needs to
        else:
            reboot()


def disable_selinux():
    sudo("sed -i 's/\=enforcing/\=permissive/g' /etc/selinux/config")
    print("!-"*50)
    print("Now you need to restart the system.")


def setup_project_directory():
    make_dir('/opt/sharkeyes/')
    sudo('chgrp -R sharkeyes /opt/sharkeyes')
    sudo('chmod -R 770 /opt/sharkeyes')


def setup_media_directory():
    if not exists('/opt/sharkeyes/media/'):
        make_dir('/opt/sharkeyes/media/')
    with cd('/opt/sharkeyes/media'):
        for d in ['netcdf', 'unchopped', 'vrt_files', 'tiles', 'keys']:
            if not exists(d):
                make_dir(d)
    if not env.user == 'vagrant':
        sudo('chgrp -R sharkeyes /opt/sharkeyes/media')
        sudo('chmod -R 774 /opt/sharkeyes/media')


def install_geotools():
    sudo('yum -y install lapack atlas atlas-devel')
    sudo('yum -y install blas-devel lapack-devel libpng-devel')
    sudo('yum -y --nogpgcheck install geos-devel proj')
    sudo('yum -y install rabbitmq-server')

    if not exists('/opt/installers/gdal-1.10.1/install_complete'):
        with cd('/opt/installers'):
            sudo('wget http://download.osgeo.org/gdal/1.10.1/gdal-1.10.1.tar.gz')
            sudo('tar -xvzf gdal-1.10.1.tar.gz')
        with cd('/opt/installers/gdal-1.10.1/'):
            sudo('./configure --prefix=/usr/local')
            sudo('make && make install')
            sudo('touch install_complete')

    sudo("if grep -Fxq '/usr/local/lib' '/etc/ld.so.conf'; then :; else echo '/usr/local/lib' | tee -a /etc/ld.so.conf; fi")
    sudo('ldconfig')

    # link proj
    if(is_64()):
        if not exists('/usr/lib64/libproj.so'):
            sudo('ln -s /usr/lib64/libproj.so.0 /usr/lib64/libproj.so')
    else:
        if not exists('/usr/lib/libproj.so'):
            sudo('ln -s /usr/lib/libproj.so.0 /usr/lib/libproj.so')


def setup_python():
    with cd('/opt/sharkeyes/'):
        if not exists('env_sharkeyes'):
            run('virtualenv -p /usr/bin/python2.7 env_sharkeyes')
        for package in python_packages:
            run('env_sharkeyes/bin/pip install ' + package)
        run('env_sharkeyes/bin/pip install -e git+https://github.com/matplotlib/basemap#egg=Basemap')
    if not exists('/opt/sharkeyes/env_sharkeyes/lib/python2.7/site-packages/mpl_toolkits/basemap'):
        run('ln -s /opt/sharkeyes/env_sharkeyes/src/basemap/lib/mpl_toolkits/basemap' + ' ' +   # explicit space because I fail
            '/opt/sharkeyes/env_sharkeyes/lib/python2.7/site-packages/mpl_toolkits/basemap')
    if not exists('/opt/.mpl_tmp'):
        make_dir('/opt/.mpl_tmp')
        sudo('chgrp -R sharkeyes /opt/.mpl_tmp')
    sudo('chmod -R 770 /opt/.mpl_tmp')


def clone_repo():
    if exists('/vagrant/') and not exists('/opt/sharkeyes/src/'):     # then this is a vm, with a vagrant folder
        sudo('ln -s /vagrant /opt/sharkeyes/src')
    elif not exists('/opt/sharkeyes/src'):
        run('git clone git@github.com:avaleske/SharkEyes.git /opt/sharkeyes/src')
        with cd('/opt/sharkeyes/src/'):
            run('git checkout ' + env.branch)


def configure_mod_wsgi():
    if not exists('/etc/httpd/modules/mod_wsgi.so'):
        with cd('/opt/installers'):
            if not exists('mod_wsgi-4.2.7'):
                sudo('wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.2.7.tar.gz')
                sudo('tar xvfz 4.2.7.tar.gz')
            with cd('mod_wsgi-4.2.7'):
                with shell_env(LD_RUN_PATH='/usr/local/lib'):
                    python_path = run('which python2.7')
                    sudo('./configure --with-python=' + python_path)
                    sudo('make')
                    sudo('make install')
    if not exists('/opt/.python_eggs'):
        make_dir('/opt/.python_eggs')
        sudo('chgrp -R sharkeyes /opt/.python_eggs')
        sudo('chmod -R 770 /opt/.python_eggs')

    with settings(warn_only=True):
        with cd('/etc/httpd/conf/'):
            if run('grep -x "LoadModule wsgi_module modules/mod_wsgi.so" httpd.conf').return_code != 0:
                # get the line number where the module loading happens, and then add the load for wsgi at that point
                line_num = int(run('grep -n "# LoadModule " httpd.conf -m 1').split(':')[0]) + 3 # to get out of comments
                sudo(' gawk \'{print;if(NR==' + str(line_num) + ')print"LoadModule wsgi_module modules/mod_wsgi.so"}\' httpd.conf>httpd.conf.temp')
                sudo('cp httpd.conf httpd.conf.bak')
                sudo('mv httpd.conf.temp httpd.conf')
    # setup deamon mode
    # by doing this:https://code.google.com/p/modwsgi/wiki/QuickConfigurationGuide#Delegation_To_Daemon_Process


def configure_apache():
    #todo overwrites the one there. Should be different for local vs staging vs production
    sudo('cp /opt/sharkeyes/src/config/apache/sharkeyes /etc/httpd/sites-available/')
    # and symlink to sites-enabled as per best practices
    if not exists('/etc/httpd/sites-enabled/sharkeyes'):
        sudo('ln -s /etc/httpd/sites-available/sharkeyes /etc/httpd/sites-enabled/sharkeyes')
    with settings(warn_only=True):
        if sudo('grep -x "NameVirtualHost \*:80" /etc/httpd/conf/httpd.conf').return_code != 0:
            sudo('echo "NameVirtualHost *:80" >> /etc/httpd/conf/httpd.conf')
        if sudo('grep -x "Include /etc/httpd/sites-enabled/" /etc/httpd/conf/httpd.conf').return_code != 0:
            sudo('echo "Include /etc/httpd/sites-enabled/" >> /etc/httpd/conf/httpd.conf')
        if sudo('grep -x "WSGIPythonEggs /opt/.python_eggs/" /etc/httpd/conf/httpd.conf').return_code != 0:
            sudo('echo "WSGIPythonEggs /opt/.python_eggs/" >> /etc/httpd/conf/httpd.conf')
    sudo('service httpd restart')


def configure_mysql():
    sudo('service mysqld start')
    print("!-"*50)
    if exists('/opt/sharkeyes/src/config/mysql_setup_script_run.guard'):
        print("MySQL setup has already run successfully. If you need to run it again, delete /opt/sharkeyes/src/config/mysql_setup_script_run.guard")
    else:
        confirm("You will now start with interactive MySQL secure installation."
                    " If this is the first run, the current root password is blank. "
                    "Even if this is your local, "
                    "change it, and save the new one to your password manager. Then "
                    "answer with default answers (Y) to all other questions. Ready?")
        sudo('/usr/bin/mysql_secure_installation')
        sudo('service mysqld restart')
        root_pass = getpass('So this script can stop bugging you, first enter your root mysql password: ')
        sharkeyes_pass = getpass('And now the database password you specified in settings_local.py: ')

        with settings(warn_only=True):
            if run('mysql --user=root --password={0} -e "show databases;" | grep sharkeyes'.format(root_pass)).return_code != 0:
                run('mysql --user=root --password={0} -e "CREATE DATABASE sharkeyes;"'.format(root_pass))
            if run('mysql --user=root --password={0} -e "SELECT user from mysql.user;" | grep sharkeyes'.format(root_pass)).return_code != 0:
                run('mysql --user=root --password={0} -e "CREATE USER \'sharkeyes\'@\'localhost\' IDENTIFIED BY \'{1}\';"'.format(
                    root_pass, sharkeyes_pass))
                # assuming if we created the user already, then we already gave it proper permissions
                run('mysql --user=root --password={0} -e "GRANT ALL ON sharkeyes.* to  \'sharkeyes\'@\'localhost\';"'.format(
                    root_pass))
                run('mysql --user=root --password={0} -e "FLUSH PRIVILEGES;"'.format(root_pass))

        # touch a file to note that we don't have to do all this again.
        run('echo "This file notes that MySQL setup ran successfully. If you need to run it again, then delete this file." > '
            '/opt/sharkeyes/src/config/mysql_setup_script_run.guard')


def configure_rabbitmq():
    sudo('service rabbitmq-server start')
    sudo('service rabbitmq-server restart') # so new logins work.
    with settings(warn_only=True):
        if sudo('rabbitmqctl list_vhosts | grep sharkeyes').return_code != 0:
            sudo('rabbitmqctl add_vhost sharkeyes')
        if sudo('rabbitmqctl list_users | grep sharkeyes').return_code != 0:
            rabbit_pass = getpass("What's the Broker password you specified in settings_local.py?: ")
            sudo('rabbitmqctl add_user sharkeyes {0}'.format(rabbit_pass))
            sudo('rabbitmqctl set_permissions -p sharkeyes sharkeyes ".*" ".*" ".*"')
        if sudo('rabbitmqctl list_users | grep guest').return_code == 0:
            sudo('rabbitmqctl delete_user guest')
    sudo('usermod -a -G sharkeyes rabbitmq')


def configure_celery():
    with settings(warn_only=True):
        if run('grep celery /etc/passwd').return_code != 0:
            sudo('useradd celery')
    sudo('usermod -a -G sharkeyes celery')
    sudo('cp /opt/sharkeyes/src/config/celeryd/celeryd.sysconfig /etc/sysconfig/celeryd')
    sudo('cp /opt/sharkeyes/src/config/celeryd/celeryd /etc/init.d/celeryd')
    sudo('cp /opt/sharkeyes/src/config/celeryd/celerybeat /etc/init.d/celerybeat')
    sudo('chmod +x /etc/sysconfig/celeryd')
    sudo('chmod +x /etc/init.d/celeryd')
    sudo('chmod +x /etc/init.d/celerybeat')
    sudo('service celeryd start')
    sudo('service celerybeat start')


def deploy():
    with cd('/opt/sharkeyes/src/'):
        if not exists('/vagrant/'): # then this is not a local vm
            run('git status')
            branch = prompt("Branch to run? (Enter to leave unchanged): ")
            if branch:
                run('git checkout {0}'.format(branch))
            run('git pull')
        with prefix('source /opt/sharkeyes/env_sharkeyes/bin/activate'):
            print("!-"*50)
            print("If this is your first run, Django will ask you to create a super user. "
                    "Store the password in your password manager.")
            run('./manage.py syncdb')
            run('./manage.py migrate djcelery 0004')
            run('./manage.py migrate pl_download')
            run('./manage.py migrate pl_plot')
            run('./manage.py loaddata initial_data.json')
            run('./manage.py migrate pl_chop')
            run('./manage.py collectstatic')
    sudo('service httpd restart') #replace this with touching wsgi after we deamonize that


def set_all_to_start_on_startup():
    for service in ['mysqld', 'httpd', 'rabbitmq-server', 'celeryd', 'celerybeat']:
        sudo('/sbin/chkconfig {0} on'.format(service))
    if env.user == 'vagrant':
        sudo('/sbin/chkconfig httpd off')
        sudo('/sbin/chkconfig celerybeat off')


def restartsite():
    # starts everything that needs to run for the production environment
    sudo('service mysqld restart')
    sudo('service rabbitmq-server restart')
    sudo('service celeryd restart')
    sudo('service celerybeat restart')
    sudo('service httpd restart')
    print("!-"*50)
    prompt("And you're good to go! Hit enter to continue.")


def startdev():
    # starts everything that needs to run for the dev environment
    sudo('service mysqld start')
    sudo('service rabbitmq-server start')
    sudo('service celeryd start')
    sudo('service celerybeat stop') # stop celerybeat so it doesn't run the main task
    sudo('service httpd stop')  # stop apache so it's not in the way
    print("!-"*50)
    prompt("And you're good to go! Hit enter to continue.")


def runserver():
    with cd('/opt/sharkeyes/src'):
        run('./runserver.sh')


def provision():
    install_prereqs()
    install_python27()
    install_apache()
    install_mysql()
    setup_group()
    disable_selinux()
    setup_project_directory()
    setup_media_directory()
    install_geotools()
    setup_python()
    clone_repo()
    configure_mod_wsgi()
    configure_apache()
    configure_mysql()
    configure_rabbitmq()
    configure_celery()
    set_all_to_start_on_startup()
    deploy()
    print("!-"*50)
    print("And provisioning is complete. Awesome! Just restart the system (so selinux is turned off) and you'll be good.")


def uname():
    run('uname -a')


def make_dir(path):
    if not exists(path):
        sudo('mkdir ' + path)


def is_64():
    if run('uname -m') == 'x86_64':
        return True
    return False

def is_centos_7():
    if 'release 7' in run('cat /etc/redhat-release'):
        return True
    return False

def restart():
        reboot()