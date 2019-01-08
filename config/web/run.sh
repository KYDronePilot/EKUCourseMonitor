#!/usr/bin/env bash

# Apply migrations.
python /src/manage.py makemigrations
python /src/manage.py migrate
# Start monitor daemon.
/usr/local/bin/python /src/monitor/monitoring_core/monitor.py &
# Start Gunicorn
/bin/bash /run/gunicorn_start
