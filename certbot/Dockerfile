FROM ubuntu:latest

# FQDN of the server.
ENV FQDN <host.domain>

# Email used with certbot.
ENV EMAIL <user@example.com>

# Install certbot.
RUN apt-get update && \
    apt-get install software-properties-common -y && \
    add-apt-repository universe && \
    add-apt-repository ppa:certbot/certbot && \
    apt-get update && \
    apt-get install python-certbot-nginx wget -y

# Directory for cert params and certs.
RUN mkdir /cert_params /certs

# Expose port 80 for getting the cert.
EXPOSE 80

WORKDIR /src

CMD ["/bin/bash", "/src/run.sh"]