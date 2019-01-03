#!/bin/bash

chmod u+x /run/gunicorn_start
python manage.py makemigrations
python manage.py migrate

/bin/bash /run/gunicorn_start
