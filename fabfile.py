#!/usr/bin/env python

from fabric.api import run, env, sudo, local
from fabric.contrib.console import confirm


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
    sudo('yum -y update')                               # careful here if not on a new machine
    sudo('yum -y groupinstall "Development tools"')
    sudo('yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel')
    sudo('yum -y install centos-release-SCL')

def uname():
    run('uname -a')

