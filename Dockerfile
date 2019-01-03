FROM ubuntu:latest

WORKDIR /usr/src/code

COPY . .

RUN /bin/bash setup.sh

EXPOSE 8080
