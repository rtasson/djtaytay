FROM		debian:latest
LABEL           maintainer="rjt@lowhangingfru.it"

WORKDIR         /srv/djtaytay

RUN             apt-get update -qq
RUN             apt-get install -qqy ffmpeg
RUN             apt-get install -qqy python3
RUN             apt-get install -qqy python3-setuptools
RUN             apt-get install -qqy python3-pip

COPY            requirements.txt requirements.txt

RUN             /usr/bin/pip3 install -r requirements.txt

COPY            . .

EXPOSE          8000
CMD             ["gunicorn", "--workers=4", "--worker-class=eventlet", "--bind=0.0.0.0:8000", "djtaytay:app"]
