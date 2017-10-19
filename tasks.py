# Copyright 2017, Dell EMC, Inc.
from service.ucs import Ucs
from celery import Celery
import requests
import json

amqp = "amqp://localhost"
app = Celery("tasks", broker=amqp)

app.conf.update(worker_concurrency=4)

# load config info
try:
    with open('config.json') as config_data:
        config = json.load(config_data)
except:
    print("Error loading config.json, using defaults!")
    config = {
        "callbackUrl": "http://10.62.59.210:8080/api/current/ucsCallback"
    }

callbackUrl = config['callbackUrl']


@app.task
def add(x, y):
    print 'add function starting...'
    import time
    print 'start sleep 10s...'
    time.sleep(10)
    print 'end sleep 10s...'
    z = x + y
    print z
    print 'add function ending...'
    print 'start to send http request to on-http'


@app.task
def systemGetAll_(headers, taskId):
    result = Ucs.systemGetAll(headers)
    sendHttpRequest.delay(taskId, result)


@app.task
def systemGetAll(funcName, taskId, *args, **kwargs):
    result = getattr(Ucs, funcName)(*args, **kwargs)
    print result
    sendHttpRequest.delay(taskId, result)


@app.task
def sendHttpRequest(taskId, data):
    url = callbackUrl
    querystring = {"taskId": taskId}
    headers = {
        'content-type': "application/json",
    }
    requests.request(
        "POST", url, data=data, headers=headers, params=querystring)


if __name__ == "__main__":
    app.start()
