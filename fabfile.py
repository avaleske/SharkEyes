#!/usr/bin/env python

from fabric.api import run, env, sudo, local, cd, settings
from fabric.contrib.console import confirm
from fabric.contrib.files import exists


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
    # sudo('yum -y update')                               # careful here if not on a new machine
    sudo('yum -y groupinstall "Development tools"')
    sudo('yum -y install wget zlib-devel bzip2-devel openssl-devel ncurses-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel')
    # sudo('yum -y install centos-release-SCL')         # let's not do this, so we have more control over things

    # repos
    with settings(warn_only=True):
        with cd('/opt'):
            if run('rpm -q epel-release-6-8.noarch').return_code != 0:
                sudo('wget http://mirror-fpt-telecom.fpt.net/fedora/epel/6/i386/epel-release-6-8.noarch.rpm')
                sudo('rpm -ivh epel-release-6-8.noarch.rpm')
            if run('rpm -q elgis-release-6-6_0.noarch').return_code != 0:
                sudo('wget http://elgis.argeo.org/repos/6/elgis-release-6-6_0.noarch.rpm')
                sudo('rpm -Uvh elgis-release-6-6_0.noarch.rpm')


def install_python27():
    if not exists('/usr/bin/python2.7'):
        with cd('/opt/'):
            sudo('wget https://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz')
            sudo('tar -xvzf Python-2.7.3.tgz')
        with cd('/opt/Python-2.7.3/'):
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
    sudo('yum -y install httpd-devel.x86_64')


def install_mysql():
    sudo('yum -y install mysql')
    sudo('yum -y mysql-python')
    sudo('yum -y mysql-server')


def install_geo_tools():
    sudo('yum -y install blas-devel freetype-devel lapack-devel libpng-devel')
    sudo('yum -y install geos-devel proj')
    sudo('yum -y install rabbitmq-server')

    if not exists('/opt/gdal-1.10.1/install_complete'):
        with cd('/opt'):
            sudo('wget http://download.osgeo.org/gdal/1.10.1/gdal-1.10.1.tar.gz')
            sudo('tar -xvzf gdal-1.10.1.tar.gz')
        with cd('/opt/gdal-1.10.1/'):
            sudo('./configure --prefix=/usr/local')
            sudo('make && make install')
            sudo('touch install_complete')

    sudo("if grep -Fxq '/usr/local/lib' '/etc/ld.so.conf'; then :; else echo '/usr/local/lib' | tee -a /etc/ld.so.conf; fi")
    sudo('ldconfig')

def setup_python():
    pass


def configure_apache():
    pass


def configure_mod_wsgi():
    pass


def configure_mysql():
    pass


def deploy():
    pass


def provision():
    install_prereqs()
    install_python27()
    install_apache()
    install_mysql()
    install_geo_tools()
    setup_python()
    configure_apache()
    configure_mod_wsgi()
    configure_mysql()


def uname():
    run('uname -a')

