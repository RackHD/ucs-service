
[![Coverage Status](https://coveralls.io/repos/github/RackHD/ucs-service/badge.svg?branch=master)](
https://coveralls.io/github/RackHD/ucs-service?branch=master)

# ucs-service

‘ucs-service’ is a module used by RackHD to interface with hardware being managed by a Cisco UCS manager.
RackHD can retrieve UCS hardware data via http/https APIs of ucs-service, ucs-service will then send request to Cisco UCS manager to collect data and return to RackHD.
Besides synchronous APIs, ucs-service also provides asynchronous API which can solve UCSM slow response problem. Celery is used as task queue for asynchronous API design.

Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.

## installation

    pip install -r requirements.txt

**Note**: Celery requires a broker and RabbitMQ is chosen. RabbitMQ is not included in requirement.txt, user should install RabbitMQ separately.

## configuration

Before user starts ucs-service, there are some configurations should be set:

* **address**: network address ucs service will listen.
* **port**: network port ucs service will listen.
* **httpsEnable**: if set to true, https will be used. Other wise http will be used.
* **keyFile**: key file for https.
* **certFile** certification file for https.
* **callbackUrl**: RackHD callback API. ucs-service asynchronous API will post data to RackHD via this callback.
* **concurrency**: Celery concurrent process number, default is 2.
* **session**: After ucs-service login UCSM, it will keep login active for a duration of "session", default it is 60 seconds.

All configurations are stored in config.json, in the root path of ucs-service directory.

## start the service

To start the service:

    python app.py
    python task.py worker

If you have supervisord available, you can use ucs-service-ctl.sh to start the service:

    sudo ./ucs-service-ctl.sh start

Script ucs-service-ctl.sh can also be used to stop the service:

    sudo ./ucs-service-ctl.sh stop

## testing

To run unit tests:

    python -m unittest discover -s tests/unit_tests

To run functional tests, you should start UCS-service, go to tests/function_tests/ and run:

    sudo bash run_test.sh <UCSM_IP> <UCSM_USER> <UCSM_PASS>

## Running in docker
RabbitMQ is not included in docker, user should install RabbitMQ separately.
Because of ucs-service's callback mechanism, it needs to communicate with RackHD host, so ucs-service in docker should run in host mode.

    sudo docker build -t example/ucs-service .
    sudo docker run -ti --net=host --rm example/ucs-service

## Licensing

Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

RackHD is a Trademark of Dell EMC
