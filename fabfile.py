#!/usr/bin/env python

from fabric.api import run, env, sudo, local, cd
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


def install_mysql():
    pass


def install_geo_tools():
    pass


def setup_python():
    pass


def setup_apache():
    pass


def setup_mod_wsgi():
    pass


def deploy():
    pass


def provision():
    install_prereqs()
    install_python27()
    install_mysql()
    install_geo_tools()
    setup_python()
    setup_apache()
    setup_mod_wsgi()
    deploy()


def uname():
    run('uname -a')

