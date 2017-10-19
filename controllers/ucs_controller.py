# Copyright 2017, Dell EMC, Inc.
from flask import request
from service.ucs import Ucs
from util.decorator import response_wrapper, status_handler


def login_get():
    return Ucs.login_get(request.headers)


@response_wrapper
@status_handler(default_status=200)
def systemGetAll():
    return Ucs.systemGetAll(request.headers)


@response_wrapper
@status_handler(default_status=200)
def getRackmount():
    return Ucs.getRackmount(request.headers)


@response_wrapper
@status_handler(default_status=200)
def getCatalog(identifier=None):
    return Ucs.getCatalog(request.headers, identifier)


@response_wrapper
@status_handler(default_status=200)
def getPollers(identifier, classIds):
    return Ucs.getPollers(request.headers, identifier, classIds)


@response_wrapper
@status_handler(default_status=200)
def getChassis():
    return Ucs.getChassis(request.headers)


@response_wrapper
@status_handler(default_status=200)
def getServiceProfile():
    return Ucs.getServiceProfile(request.headers)


@response_wrapper
@status_handler(default_status=200)
def powerStatus(identifier=None):
    return Ucs.powerStatus(request.headers, identifier)


@response_wrapper
@status_handler(default_status=200)
def powerMgmt(identifier=None, action=None, physical=False):
    return Ucs.powerMgmt(request.headers, identifier, action, physical)
