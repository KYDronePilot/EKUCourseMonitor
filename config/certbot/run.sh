#!/usr/bin/env bash


while [true]
do
    # Generate a cert.
    certbot certonly --standalone -m mikegalliers@gmail.com --agree-tos -d docker3.galliers.org
    # Get cert params from github.
    cd /cert_params
    wget https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/options-ssl-nginx.conf
    wget https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/ssl-dhparams.pem
    # Wait 7 days before obtaining a new cert.
    sleep 604800
done
