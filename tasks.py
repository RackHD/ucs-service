# Copyright 2017, Dell EMC, Inc.

import requests
from service.ucs import Ucs
from celery import Celery
from celery.signals import worker_process_shutdown
from util.decorator import status_handler
from util import util

# Work process level global handlers to minimize UCSM login/logout actions
handlers = {}
config = util.load_config()
callbackUrl = config['callbackUrl']
amqp = config["amqp"]
app = Celery("tasks", broker=amqp)
app.conf.update(worker_concurrency=config.get("concurrency", 2))


def worker_process_cleanup(**kwargs):
    """
    Cleanup UCS handler before work processes are shutdown
    """
    util.cleanup_ucs_handler(handlers)
    print("Global handlers for celery worker process {} are cleared".format(kwargs["pid"]))


# TODO: Enhance cleanup with more stable methods
worker_process_shutdown.connect(worker_process_cleanup)


@status_handler()
def _runUcsJobCore(funcName, *args, **kwargs):
    return getattr(Ucs, funcName)(*args, **kwargs)


@app.task
def runUcsJob(funcName, callbackId, *args, **kwargs):
    """
    Run Ucs service job with given job name and arguments,
    and initiate RackHD callback task with returned job result
    """
    kwargs["handlers"] = handlers
    result = _runUcsJobCore(funcName, *args, **kwargs)
    sendHttpRequest.delay(callbackId, result)


@app.task
def sendHttpRequest(callbackId, data):
    """
    Post data to RackHD via callbackUrl
    """
    url = callbackUrl
    query_string = {"callbackId": callbackId}
    headers = {'content-type': "application/json"}
    res = requests.request(
        "POST", url, json={"body": data[0]}, headers=headers, params=query_string
    )
    if res.status_code != 200:
        print("Error to post data back to RackHD via API: {}".format(callbackUrl))
        print(res.content)


if __name__ == "__main__":
    app.start()
