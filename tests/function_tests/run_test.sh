#!/bin/bash
# Copyright 2017, Dell, Inc.

# Copyright 2017, Dell, Inc.

ucs_user=ucspe
ucs_pass=ucspe

if [ -z $1 ]
then
    echo "Error: UCS host IP should be specified"
    exit 1
fi

if [ -n $2 ]
then
    ucs_user=$2
fi

if [ -n $3 ]
then
    ucs_pass=$3
fi

virtualenv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
export UCSCONFIG="{\"ucs-host\": \"$1\", \"ucs-pass\": \"$ucs_pass\", \"ucs-user\": \"$ucs_user\"}"
nosetests -v --with-nosedep test_ucs_api

