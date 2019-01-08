FROM python:3.6

# Set Python unbuffered.
ENV PYTHONUNBUFFERED 1

# Create necessary directories.
RUN mkdir /config /logs

# Add necessary files.
ADD config/web/requirements.pip /config
ADD config/web/gunicorn_start /run
ADD config/web/setup.sh /run
ADD config/web/run.sh /run

# Add the project.
ADD EKUCourseMonitorWebpage /src

# Run setup script.
RUN /bin/bash /run/setup.sh

WORKDIR /src
