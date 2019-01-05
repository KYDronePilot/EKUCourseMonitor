FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /config /logs

ADD config/web/requirements.pip /config
ADD config/web/gunicorn_start /run
ADD config/web/setup.sh /run

RUN pip install -r /config/requirements.pip
RUN mkdir /src

WORKDIR /src
