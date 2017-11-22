# Copyright 2017, Dell EMC, Inc.
FROM ubuntu:16.04
WORKDIR /usr/src/app
RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    python3-dev \
    libffi-dev \
    libssl-dev
COPY . .
RUN pip3 install -U setuptools==36.7.2
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 7080
ENTRYPOINT sh docker-entrypoint.sh
