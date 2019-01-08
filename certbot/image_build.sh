#!/usr/bin/env bash

# Move to directory of script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${DIR}

# Build the certbot image.
docker build -t ecm_certbot_image .

# Get absolute paths of directories.
CERTS=$(realpath "./certs")
CERT_PARAMS=$(realpath "./cert_params")
RUN=$(realpath "./run")

# Create a container.
docker create -p 80:80 --name ecm_certbot_live \
        -v ${CERTS}:/certs \
        -v ${CERT_PARAMS}:/cert_params \
        -v ${RUN}:/src ecm_certbot_image
