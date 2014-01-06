#!/bin/bash

virtualenv ~/py2.7 -p /usr/local/bin/python2.7
source ~/py2.7/bin/activate
pip install Django
#pip install psycopg2