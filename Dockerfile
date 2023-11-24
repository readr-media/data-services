FROM python:3.9-slim

COPY .  /usr/src/app/data-service
WORKDIR  /usr/src/app/data-service

RUN addgroup user && adduser -h /home/user -D user -G user -s /bin/sh

RUN apt-get update \
    && apt-get install -y gcc libc-dev libxslt-dev libxml2 libpq-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

RUN apk add --no-cache tzdata

ENV TZ="Asia/Taipei"

ENV LC_ALL="en_US.utf8" 
ENV LANG=en_US.UTF-8
ENV PYTHONIOENCODING=utf8


EXPOSE 8080
CMD [ "env", "LC_ALL='en_US.utf-8'", "/usr/local/bin/uwsgi", "--ini", "server.ini"]
