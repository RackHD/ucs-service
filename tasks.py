# Copyright 2017, Dell EMC, Inc.
from celery import Celery
from service.ucs import Ucs
from util.decorator import status_handler

amqp = 'amqp://localhost'
app = Celery('tasks', broker=amqp)


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
    return z


@app.task
@status_handler(default_status=200)
def systemGetAll(headers):
    service = Ucs()
    result = service.systemGetAll(headers)
    sendHttpRequest.delay(result)
    return result


@app.task
def sendHttpRequest(content):
    print 'start to send request...'
    print content
    print 'finished...'


if __name__ == "__main__":
    app.start()
