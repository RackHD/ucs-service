# Copyright 2017, Dell EMC, Inc.

import tasks
from flask import request
from util.decorator import response_wrapper, status_handler
from util.util import serialize_ucs_http_headers


@response_wrapper
@status_handler(default_status=202)
def getPollersAsync(identifier, classIds, taskId):
    """Get pollers asynchronously"""
    tasks.runUcsJob.delay(
        "getPollers",
        taskId,
        serialize_ucs_http_headers(request.headers),
        identifier,
        classIds
    )
    return {"data": "Accepted"}
