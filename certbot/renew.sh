#!/usr/bin/env bash

# For renewing certs.

# Move to project directory.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${DIR}/../

# Stop Nginx while getting new cert.
docker-compose stop nginx

# Renew cert.
docker start -ai ecm_certbot_live

# Start Nginx back up.
docker-compose start nginx
