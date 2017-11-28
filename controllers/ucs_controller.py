# Copyright 2017, Dell EMC, Inc.

from flask import request, current_app
from service.ucs import Ucs
from util.decorator import response_wrapper, status_handler


def login_get():
    return Ucs.login_get(request.headers)


@response_wrapper
@status_handler(default_status=200)
def systemGetAll():
    handlers = current_app.config.get("handlers")
    return Ucs.systemGetAll(request.headers, handlers=handlers)


@response_wrapper
@status_handler(default_status=200)
def getRackmount():
    handlers = current_app.config.get("handlers")
    return Ucs.getRackmount(request.headers, handlers=handlers)


@response_wrapper
@status_handler(default_status=200)
def getCatalog(identifier=None):
    handlers = current_app.config.get("handlers")
    return Ucs.getCatalog(request.headers, identifier, handlers=handlers)


@response_wrapper
@status_handler(default_status=200)
def getPollers(identifier, classIds):
    handlers = current_app.config.get("handlers")
    return Ucs.getPollers(
        request.headers, identifier, classIds, handlers=handlers)


@response_wrapper
@status_handler(default_status=200)
def getChassis():
    handlers = current_app.config.get("handlers")
    return Ucs.getChassis(request.headers, handlers=handlers)


@response_wrapper
@status_handler(default_status=200)
def getServiceProfile():
    handlers = current_app.config.get("handlers")
    return Ucs.getServiceProfile(request.headers, handlers=handlers)


@response_wrapper
@status_handler(default_status=200)
def powerStatus(identifier=None):
    handlers = current_app.config.get("handlers")
    return Ucs.powerStatus(request.headers, identifier, handlers=handlers)


@response_wrapper
@status_handler(default_status=200)
def powerMgmt(identifier=None, action=None, physical=False):
    handlers = current_app.config.get("handlers")
    return Ucs.powerMgmt(request.headers, identifier, action, physical, handlers=handlers)
