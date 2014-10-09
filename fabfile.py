#!/usr/bin/env python

# If running this on a critical system that shouldn't reboot, comment out the reboot() command in setup_group()
# The script will fail with a permissions error at that point, just run it again from the start and it will work.

# Before running this, make sure you've filled out settings_local.py.
# If you're running this against a production server, then make sure you've also set up git ssh keys with github.

# Finally, all the functions that'd you'd expect to be should be idempotent, save for configure_apache(), which
# will overwrite /etc/httpd/sites-available/sharkeyes with whatever's in the config/apache folder of the project.

from fabric.api import run, env, sudo, local, cd, settings, prefix, reboot
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.context_managers import shell_env

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


def install_prereqs():
    make_dir('/opt/installers')
    # repos
    with settings(warn_only=True):
        with cd('/opt/installers'):
            if run('rpm -q epel-release-6-8.noarch').return_code != 0:
                if is_64():
                    sudo('wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm')
                else:
                    sudo('wget http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm')
                sudo('rpm -ivh epel-release-6-8.noarch.rpm')
            if run('rpm -q elgis-release-6-6_0.noarch').return_code != 0:
                sudo('wget http://elgis.argeo.org/repos/6/elgis-release-6-6_0.noarch.rpm')
                sudo('rpm -Uvh elgis-release-6-6_0.noarch.rpm')

    # sudo('yum -y update')                               # careful here if not on a new machine
    sudo('yum -y groupinstall "Development tools"')
    sudo('yum -y install vim emacs man wget zlib-devel bzip2-devel openssl-devel ncurses-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel')

    """
    if not run('freetype-config --ftversion').startswith('2.4'):    # we want at least version 2.4
        with cd('/opt/installers'):
            if not exists('freetype-2.4.2.tar.gz'):
                sudo('wget http://download.savannah.gnu.org/releases/freetype/freetype-2.4.2.tar.gz')
                sudo('tar -xvzf freetype-2.4.2.tar.gz')
        with cd('/opt/installers/freetype-2.4.2'):
            sudo('./configure --prefix=/usr')
            sudo('make')
            sudo('make install')
            """
    # sudo('yum -y install centos-release-SCL')         # let's not do this, so we have more control over things


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
    sudo('yum -y install mysql mysql_devel')
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
        reboot()


def setup_project_directory():
    make_dir('/opt/sharkeyes/')
    sudo('chgrp -R sharkeyes /opt/sharkeyes')
    sudo('chmod -R 770 /opt/sharkeyes')


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
        #with prefix('source env_sharkeyes/bin/activate'):
        #sudo('source env_sharkeyes/bin/activate')
        for package in python_packages:
            run('env_sharkeyes/bin/pip install ' + package) # tried to use requirements.txt and it kept failing
        run('env_sharkeyes/bin/pip install -e git+https://github.com/matplotlib/basemap#egg=Basemap')
        if not exists('env_sharkeyes/lib/python2.7/site-packages/mpl_toolkits/basemap'):
            run('ln -s env_sharkeyes/src/basemap/lib/mpl_toolkits/basemap/ env_sharkeyes/lib/python2.7/site-packages/mpl_toolkits/basemap')


def clone_repo():
    if exists('/vagrant/') and not exists('/opt/sharkeyes/src/'):     # then this is a vm, with a vagrant folder
        sudo('ln -s /vagrant /opt/sharkeyes/src')
    elif not exists('/opt/sharkeyes/src'):
        run('git clone git@github.com:avaleske/SharkEyes.git /opt/sharkeyes/src')


def configure_mod_wsgi():
    if not exists('/etc/httpd/modules/mod_wsgi.so'):
        with cd('/opt/installers'):
            if not exists('mod_wsgi-4.2.7'):
                sudo('wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.2.7.tar.gz')
                sudo('tar xvfz 4.2.7.tar.gz')
            with cd('mod_wsgi-4.2.7'):
                with shell_env(LD_RUN_PATH='/usr/local/lib'):
                    sudo('./configure --with-python=/usr/local/bin/python2.7')
                    sudo('make')
                    sudo('make install')

    with settings(warn_only=True):
        with cd('/etc/httpd/conf/'):
            if run('grep -x "LoadModule wsgi_module modules/mod_wsgi.so" httpd.conf').return_code != 0:
                # get the line number where the module loading happens, and then add the load for wsgi at that point
                line_num = run('grep -n "^LoadModule " httpd.conf -m 1').split(':')[0]
                sudo(' gawk \'{print;if(NR==' + line_num + ')print"LoadModule wsgi_module modules/mod_wsgi.so"}\' httpd.conf>httpd.conf.temp')
                sudo('cp httpd.conf httpd.conf.bak')
                sudo('mv httpd.conf.temp httpd.conf')
    # setup deamon mode
    pass

def configure_apache():
    sudo('cp /opt/sharkeyes/src/config/apache/sharkeyes /etc/httpd/sites-available/')
    # and symlink to sites-enabled as per best practices
    if not exists('/etc/httpd/sites-enabled/sharkeyes'):
        sudo('ln -s /etc/httpd/sites-available/sharkeyes /etc/httpd/sites-enabled/sharkeyes')
    with settings(warn_only=True):
        if sudo('grep -x "NameVirtualHost \*:80" /etc/httpd/conf/httpd.conf').return_code != 0:
            sudo('echo "NameVirtualHost *:80" >> /etc/httpd/conf/httpd.conf')
        if sudo('grep -x "Include /etc/httpd/sites-enabled/" /etc/httpd/conf/httpd.conf').return_code != 0:
            sudo('echo "Include /etc/httpd/sites-enabled/" >> /etc/httpd/conf/httpd.conf')
    sudo('service httpd restart')
    # do stuff from here: http://twohlix.com/2011/05/setting-up-apache-virtual-hosts-on-centos/
    # edit virtual hosts to point to right place
    # need to point at django settings file?



def configure_mysql():
    # secure installation
    # edit password stuff
    # create database
    pass


def configure_rabbitmq():
    # do the thing
    # deamon mode
    pass


def deploy():
    # checkout code, or link to /vagrant, depending.
    # manage.py migrate and stuff
    # start rabbit, celery
    pass


def provision():
    install_prereqs()
    install_python27()
    install_apache()
    install_mysql()
    setup_group()
    setup_project_directory()
    install_geotools()
    setup_python()
    configure_mod_wsgi()
    configure_apache()
    configure_mysql()


def uname():
    run('uname -a')


def make_dir(path):
    if not exists(path):
        sudo('mkdir ' + path)

def is_64():
    if run('uname -m') == 'x86_64':
        return True
    return False
