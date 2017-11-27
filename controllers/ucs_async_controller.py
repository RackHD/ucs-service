# Copyright 2017, Dell EMC, Inc.

import tasks
from flask import request
from util.decorator import response_wrapper, status_handler
from util.util import serialize_ucs_http_headers


@response_wrapper
@status_handler(default_status=202)
def getPollersAsync(identifier, classIds, callbackId):
    """Get pollers asynchronously"""
    tasks.runUcsJob.delay(
        "getPollers",
        callbackId,
        serialize_ucs_http_headers(request.headers),
        identifier,
        classIds
    )
    return {"data": "Accepted"}


@response_wrapper
@status_handler(default_status=202)
def getCatalogAsync(identifier, callbackId):
    """Get catalog asynchronously"""
    tasks.runUcsJob.delay(
        "getCatalog",
        callbackId,
        serialize_ucs_http_headers(request.headers),
        identifier
    )
    return {"data": "Accepted"}
