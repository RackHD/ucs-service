# Copyright 2017, Dell EMC, Inc.
FROM ubuntu:16.04
WORKDIR /usr/src/app
RUN apt-get update && \
    apt-get install -y \
    python-pip \
    python-dev \
    libffi-dev \
    libssl-dev \
    rabbitmq-server
COPY . .
RUN pip install -U setuptools==36.7.2
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 7080
ENTRYPOINT sh docker-entrypoint.sh
