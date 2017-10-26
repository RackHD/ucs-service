# Copyright 2017, Dell EMC, Inc.
import traceback
from flask import request
from service.ucs import Ucs
from ucsmsdk.ucsexception import UcsException


def login_get():
    service = Ucs()
    return service.login_get(request.headers)


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


def handle_error_decorator(function):
    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
        except UcsException as e:
            return 'Internal Server Error', e.error_descr, 500
        except Exception as e:
            return 'Internal Server Error', traceback.format_exc(e), 500

        if result.get("data"):
            return result.get("data")
        elif result.get("error") == "Forbidden":
            return result.get("error"), "", 403
        elif result.get("error") == "Couldn't fetch computeRackUnits":
            return result.get("error"), "", 500
        elif result.get("error") == "Couldn't fetch ComputeBlade":
            return result.get("error"), "", 500
        elif result.get("error") == "Couldn't fetch EquipmentChassis":
            return result.get("error"), "", 500
        elif result.get("error").startswith("Couldn't fetch "):
            return result.get("error"), "", 500
        else:
            return "Unknown", "", 500

    return wrapper


@http_body_factory
@handle_error_decorator
def systemGetAll():
    service = Ucs()
    return service.systemGetAll(request.headers)


@http_body_factory
@handle_error_decorator
def getRackmount():
    service = Ucs()
    return service.getRackmount(request.headers)


@http_body_factory
@handle_error_decorator
def getCatalog(identifier=None):
    service = Ucs()
    return service.getCatalog(request.headers, identifier)


@http_body_factory
@handle_error_decorator
def getPollers(identifier, classIds):
    service = Ucs()
    return service.getPollers(request.headers, identifier, classIds)


@http_body_factory
@handle_error_decorator
def getChassis():
    service = Ucs()
    return service.getChassis(request.headers)


@http_body_factory
@handle_error_decorator
def getServiceProfile():
    service = Ucs()
    return service.getServiceProfile(request.headers)


@http_body_factory
@handle_error_decorator
def powerStatus(identifier=None):
    service = Ucs()
    return service.powerStatus(request.headers, identifier)


@http_body_factory
@handle_error_decorator
def powerMgmt(identifier=None, action=None, physical=False):
    service = Ucs()
    return service.powerMgmt(request.headers, identifier, action, physical)
