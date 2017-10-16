# Copyright 2017, Dell EMC, Inc.
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsexception import UcsException
from ucsmsdk.mometa.ls.LsPower import LsPowerConsts
from ucsmsdk.mometa.ls.LsPower import LsPower
import traceback
from flask import request
from service.ucs import Ucs


def login_get():
    authInfo = _getUcsAuthInfo((request.headers))
    handle = UcsHandle(*authInfo, secure=False)
    if handle.login():
        return handle.cookie


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
def getServiceProfile():
    authInfo = _getUcsAuthInfo((request.headers))
    handle = UcsHandle(*authInfo, secure=False)
    if not handle.login():
        handle.logout()
        return 'Forbidden', "", 403
    rootElements = [{
        "ciscoXmlName": "orgOrg",
        "humanReadableName": "ServiceProfile"
    }]
    finalObjs = {}
    for x in rootElements:
        subElement = {}
        try:
            components = handle.query_classid(x["ciscoXmlName"])
        except UcsException as e:
            handle.logout()
            return 'Internal Server Error', e.error_descr, 500
        else:
            if not (type(components) == list):
                handle.logout()
                return "Couldn't fetch " + x["humanReadableName"], "", 500

            for y in components:
                subElement["org"] = y.level
                subElement["members"] = []
                try:
                    lsList = handle.query_children(
                        in_dn="org-root", class_id="lsServer")
                except UcsException as e:
                    handle.logout()
                    return 'Internal Server Error', e.error_descr, 500
                else:
                    if not (type(lsList) == list):
                        handle.logout()
                        return "Couldn't fetch Logical Servers", "", 500
                    for item in lsList:
                        logicalServer = {}
                        identifier = item.dn
                        obj = handle.query_dn(dn=identifier)
                        logicalServer["name"] = obj.rn
                        logicalServer["path"] = obj.dn
                        logicalServer["associatedServer"] = obj.pn_dn
                        logicalServer["assoc_state"] = obj.assoc_state
                        subElement["members"].append(logicalServer)
            finalObjs[x["humanReadableName"]] = subElement
    handle.logout()
    return finalObjs


@http_body_factory
def powerStatus(identifier=None):
    authInfo = _getUcsAuthInfo((request.headers))
    handle = UcsHandle(*authInfo, secure=False)
    if handle.login():
        try:
            state = _powerStatus(identifier, handle)
        except UcsException as e:
            handle.logout()
            return 'Internal Server Error', e.error_descr, 500
        else:
            handle.logout()
            return {"serverState": state}
    else:
        handle.logout()
        return 'Forbidden', "", 403


@http_body_factory
def getTest(no):
    print 'begin..........'
    import time
    time.sleep(5)
    print 'end..........'
    return {"success": True, "no": no}


@http_body_factory
def getTestAsync(no):
    print 'begin async...'
    from tasks import add
    add.delay(4, 4)
    print 'end async...'
    return "", 202


@http_body_factory
def powerMgmt(identifier=None, action=None, physical=False):
    authInfo = _getUcsAuthInfo((request.headers))
    handle = UcsHandle(*authInfo, secure=False)
    if handle.login():
        try:
            if physical:
                data = _physical_power_set(
                    handle=handle, dn=identifier, state=action)
            else:
                data = _service_profile_power_set(
                    handle=handle, dn=identifier, state=action)
        except UcsException as e:
            handle.logout()
            return 'Internal Server Error', e.error_descr, 500
        else:
            handle.logout()
            data = reduce(data.__dict__)
        return data
    else:
        handle.logout()
        return 'Forbidden', "", 403


def _service_profile_power_set(handle, dn=None, state=None):
    blade_mo = handle.query_dn(dn)
    if blade_mo is None:
        raise UcsException(
            "service_profile_power_set: Failed to set element power",
            "sever %s does not exist" % (dn))
    elif blade_mo._class_id == "LsServer":
        sp_mo = blade_mo
    elif blade_mo.assigned_to_dn is None or blade_mo.assigned_to_dn == "":
        raise UcsException(
            "service_profile_power_set: Failed to set element power",
            "sever %s is not associated to a service profile" % (dn))
    else:
        sp_mo = handle.query_dn(blade_mo.assigned_to_dn)
    if state == "off":
        state = LsPowerConsts.STATE_DOWN
    elif state == "on":
        state = LsPowerConsts.STATE_UP
    elif state == "cycle-immediate":
        state = LsPowerConsts.STATE_CYCLE_IMMEDIATE
    elif state == "cycle-wait":
        state = LsPowerConsts.STATE_CYCLE_WAIT
    elif state == "bmc-reset-immediate":
        state = LsPowerConsts.STATE_BMC_RESET_IMMEDIATE
    elif state == "ipmi-reset":
        state = LsPowerConsts.STATE_IPMI_RESET
    elif state == "hard-reset-immediate":
        state = LsPowerConsts.STATE_HARD_RESET_IMMEDIATE
    elif state == "soft-shut-down":
        state = LsPowerConsts.STATE_SOFT_SHUT_DOWN
    else:
        raise UcsException(
            "server_power_set: Failed to set server power",
            "action '{0}' is not valid. Choose one of the following: "
            "'on', 'off', 'cycle-wait','cycle-immediate', 'bmc-reset-immediate',"
            " 'ipmi-reset', 'hard-reset-immediate', 'soft-shut-down' ".format(
                state))
    data = LsPower(parent_mo_or_dn=sp_mo, state=state)
    handle.set_mo(sp_mo)
    handle.commit()
    return data


def _physical_power_set(handle, dn=None, state=None):
    ADMIN_POWER_ADMIN_DOWN = "admin-down"
    ADMIN_POWER_ADMIN_UP = "admin-up"
    ADMIN_POWER_BMC_RESET_IMMEDIATE = "bmc-reset-immediate"
    ADMIN_POWER_BMC_RESET_WAIT = "bmc-reset-wait"
    ADMIN_POWER_CMOS_RESET_IMMEDIATE = "cmos-reset-immediate"
    ADMIN_POWER_CYCLE_IMMEDIATE = "cycle-immediate"
    ADMIN_POWER_CYCLE_WAIT = "cycle-wait"
    ADMIN_POWER_DIAGNOSTIC_INTERRUPT = "diagnostic-interrupt"
    ADMIN_POWER_HARD_RESET_IMMEDIATE = "hard-reset-immediate"
    ADMIN_POWER_HARD_RESET_WAIT = "hard-reset-wait"
    ADMIN_POWER_IPMI_RESET = "ipmi-reset"
    ADMIN_POWER_KVM_RESET = "kvm-reset"
    ADMIN_POWER_POLICY = "policy"

    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsException("physical_power_set: Failed to set element power",
                           "sever %s does not exist" % (dn))
    elif mo._class_id == "LsServer" and mo.assigned_to_dn is not None and mo.assigned_to_dn != "":
        server_mo = handle.query_dn(mo.assigned_to_dn)
    elif mo._class_id == "ComputeRackUnit" or mo._class_id == "compuetBlade":
        server_mo = mo
    else:
        raise UcsException("physical_power_set: Failed to set element power",
                           "sever %s has an unknown class_id %s" %
                           (dn, mo._class_id))
    if state == "off":
        state = ADMIN_POWER_ADMIN_DOWN
    elif state == "on":
        state = ADMIN_POWER_ADMIN_UP
    elif state == "cycle-immediate":
        state = ADMIN_POWER_CYCLE_IMMEDIATE
    elif state == "cycle-wait":
        state = ADMIN_POWER_CYCLE_WAIT
    elif state == "bmc-reset-immediate":
        state = ADMIN_POWER_BMC_RESET_IMMEDIATE
    elif state == "bmc-reset-wait":
        state = ADMIN_POWER_BMC_RESET_WAIT
    elif state == "hard-reset-immediate":
        state = ADMIN_POWER_HARD_RESET_IMMEDIATE
    elif state == "hard-reset-wait":
        state = ADMIN_POWER_HARD_RESET_WAIT
    elif state == "ipmi-reset":
        state = ADMIN_POWER_IPMI_RESET
    elif state == "cmos-reset-immediate":
        state = ADMIN_POWER_CMOS_RESET_IMMEDIATE
    elif state == "diagnostic-interrupt":
        state = ADMIN_POWER_DIAGNOSTIC_INTERRUPT
    elif state == "kvm-reset":
        state = ADMIN_POWER_KVM_RESET
    elif state == "policy":
        state = ADMIN_POWER_POLICY
    else:
        raise UcsException(
            "_physical_power_set: Failed to set server power",
            "action '{0}' is not valid. physical power control supports states: "
            "'off', 'on', 'cycle-wait', 'cycle-immediate', bmc-reset-immediate, "
            "'bmc-reset-wait', 'hard-reset-immediate', 'hard-reset-wait', 'ipmi-reset', "
            "'cmos-reset-immediate', 'diagnostic-interrupt', 'kvm-reset', 'policy' "
            .format(state))

    server_mo.admin_power = state
    handle.set_mo(server_mo)
    handle.commit()
    return server_mo


def _powerStatus(dn, handle):
    blade_mo = handle.query_dn(dn)
    if blade_mo is None:
        raise UcsException(
            "service_profile_power_set: Failed to set element power",
            "sever %s does not exist" % (dn))
    elif blade_mo._class_id == "LsServer":
        sp_mo = blade_mo
    elif blade_mo.assigned_to_dn is None or blade_mo.assigned_to_dn == "":
        raise UcsException(
            "service_profile_power_set: Failed to set element power",
            "sever %s is not associated to a service profile" % (dn))
    else:
        sp_mo = handle.query_dn(blade_mo.assigned_to_dn)
    powerLs = LsPower(sp_mo)
    handle.set_mo(sp_mo)
    handle.commit()
    data = powerLs.state
    return data


def _getUcsAuthInfo(headers):
    host = headers.get('ucs-host')
    user = headers.get('ucs-user')
    password = headers.get('ucs-password')

    return (host, user, password)


def reduce(object):
    # remove the private propeties of an obj
    for property in object.keys():
        if (property[0] == "_"):
            del object[property]
    return object
