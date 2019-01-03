#!/bin/bash

apt-get update
apt-get install python3 python3-pip apache2 libapache2-mod-wsgi-py3 -y

pip3 install -r requirements.txt

python3 manage.py runserver 0.0.0.0:8080
