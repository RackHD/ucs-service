#!/bin/bash

# Copyright 2017, EMC, Inc.

# Run code checks (pylint, flake8, etc)
#
# Command forms:
#   mkcheck.sh
#       Runs checker and writes to to local file
#   mkcheck.sh
#
#   output file:
#        rackhd_test_check.txt
#

output_file=ucs_service_test_check.txt

status=0

# move existing output_file aside (add ~)
if [ -f ${output_file} ]; then
    mv ${output_file} ${output_file}~
fi

# make changes to flake8 parameters in .flake8 file
python2.7 -m flake8 --config=.flake8.ini --statistics --tee --output-file=${output_file}
if [ $? -ne 0 ]; then
    if [ "${format}" == "text" ]; then
        cat ${output_file}
    fi
    echo "Python checker failed.  Clean up code and retry"
    status=1
else
    echo "Python checker succeeded"
fi

exit ${status}
