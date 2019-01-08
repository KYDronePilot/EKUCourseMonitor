#!/usr/bin/env bash

# Setup environment.
#/bin/bash /run/setup.sh

# Start monitor daemon.
/usr/local/bin/python /src/monitor/monitoring_core/monitor.py &
# Start Gunicorn
/bin/bash /run/gunicorn_start
