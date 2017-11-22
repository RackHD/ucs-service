#!/bin/bash
# Copyright 2017, Dell EMC, Inc.

python3 app.py >> app.log 2>&1 &
python3 tasks.py worker >> tasks.log 2>&1
