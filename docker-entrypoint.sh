#!/bin/bash
# Copyright 2017, Dell EMC, Inc.

service rabbitmq-server start
python app.py >> app.log &
python tasks.py worker >> tasks.log
