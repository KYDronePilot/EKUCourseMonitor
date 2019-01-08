#!/usr/bin/env bash


# If there are already certs, renew them.
if find "/certs" ! -iname ".*" -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
    certbot renew
# Else, get a new cert.
else
    certbot certonly --standalone -m mikegalliers@gmail.com --agree-tos -n -d docker3.galliers.org
fi

# Remove any old certs.
rm -f /certs/*

# Copy certs to certs dir.
cd /etc/letsencrypt/live/docker3.galliers.org
for f in $(find /etc/letsencrypt/live/docker3.galliers.org -type l); do cp $(readlink ${f}) /certs; done;

# Change names of certs to be consistent.
cd /certs
if ls | grep 'fullchain[0-9]*\.pem'; then
    mv $(ls | grep '^fullchain[0-9]*\.pem') ./fullchain.pem
fi

if ls | grep 'cert[0-9]*\.pem'; then
    mv $(ls | grep '^cert[0-9]*\.pem') ./cert.pem
fi
if ls | grep 'chain[0-9]*\.pem'; then
    mv $(ls | grep '^chain[0-9]*\.pem') ./chain.pem
fi
if ls | grep 'privkey[0-9]*\.pem'; then
    mv $(ls | grep '^privkey[0-9]*\.pem') ./privkey.pem
fi

# Get cert params from certbot.
cd /cert_params
rm -f *
wget https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/options-ssl-nginx.conf
wget https://raw.githubusercontent.com/certbot/certbot/master/certbot/ssl-dhparams.pem
