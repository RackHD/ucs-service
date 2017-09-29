#!/bin/bash

function run() {
    for i in {1..20}; do
        curl http://localhost:7080/test/${i} &
    done
    wait
}

function runPoller() {
    for i in {1..20}; do
        curl -X GET \
            'http://10.62.59.210:7080/pollers?identifier=sys%2Frack-unit-1&classIds=memoryUnitEnvStats%2CprocessorEnvStats' \
            -H 'cache-control: no-cache' \
            -H 'postman-token: f463c5e7-e569-f18e-0145-97c6fe876240' \
            -H 'ucs-host: 10.62.59.173' \
            -H 'ucs-password: ucspe' \
            -H 'ucs-user: ucspe' &
    done
    wait
}
#time runPoller
time run
