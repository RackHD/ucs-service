# Copyright 2017, Dell EMC, Inc.
from tasks import add


def http_body_factory(function):
    def wrapper(*args, **kwargs):
        resp = function(*args, **kwargs)
        if (len(resp) == 3):
            http_res = {
                "message": resp[0],
                "status": resp[2],
                "stack": resp[1]
            }
            return http_res, resp[2]
        else:
            return resp

    return wrapper


@http_body_factory
def getTestAsync(no):
    print 'begin async...'
    add.delay(4, 4)
    print 'ernd async...'
    return "", 202
