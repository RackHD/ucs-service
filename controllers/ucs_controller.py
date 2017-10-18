# Copyright 2017, Dell EMC, Inc.
from flask import request
from service.ucs import Ucs
from util.decorator import response_wrapper, status_handler


def login_get():
    service = Ucs()
    return service.login_get(request.headers)


@response_wrapper
@status_handler(default_status=200)
def systemGetAll():
    service = Ucs()
    return service.systemGetAll(request.headers)


@response_wrapper
@status_handler(default_status=200)
def getRackmount():
    service = Ucs()
    return service.getRackmount(request.headers)


@response_wrapper
@status_handler(default_status=200)
def getCatalog(identifier=None):
    service = Ucs()
    return service.getCatalog(request.headers, identifier)


@response_wrapper
@status_handler(default_status=200)
def getPollers(identifier, classIds):
    service = Ucs()
    return service.getPollers(request.headers, identifier, classIds)


@response_wrapper
@status_handler(default_status=200)
def getChassis():
    service = Ucs()
    return service.getChassis(request.headers)


@response_wrapper
@status_handler(default_status=200)
def getServiceProfile():
    service = Ucs()
    return service.getServiceProfile(request.headers)


@response_wrapper
@status_handler(default_status=200)
def powerStatus(identifier=None):
    service = Ucs()
    return service.powerStatus(request.headers, identifier)


@response_wrapper
@status_handler(default_status=200)
def powerMgmt(identifier=None, action=None, physical=False):
    service = Ucs()
    return service.powerMgmt(request.headers, identifier, action, physical)
