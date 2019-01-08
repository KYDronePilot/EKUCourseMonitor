#!/bin/bash

cd /src
# Install dependencies.
pip install -r /config/requirements.pip
# Set up Gunicorn script.
chmod u+x /run/gunicorn_start
# Set up Django.
python manage.py collectstatic
