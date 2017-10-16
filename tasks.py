from celery import Celery

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
    return z
