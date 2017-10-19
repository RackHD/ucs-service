# Copyright 2017, Dell EMC, Inc.
from flask import request
import tasks
from util.decorator import response_wrapper, status_handler


def _getSerializedHeaders(headers):
    return {
        "ucs-host": headers.get("ucs-host"),
        "ucs-user": headers.get("ucs-user"),
        "ucs-password": headers.get("ucs-password")
    }


@response_wrapper
@status_handler(default_status=202)
def systemGetAllAsync(taskId):
    tasks.handleService.delay("systemGetAll", taskId,
                              _getSerializedHeaders(request.headers))
    return {"data": "Accepted"}
