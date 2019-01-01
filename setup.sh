#!/usr/bin/env bash

apt-get update
apt-get install python3.7 python3-pip

pip3 install requirements.txt

python3 manage.py runserver 0.0.0.0:8080
