# Copyright 2017, Dell EMC, Inc.

from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsexception import UcsException
from flask import request
from ucsmsdk.mometa.ls.LsPower import LsPowerConsts
from ucsmsdk.mometa.ls.LsPower import LsPower


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


@http_body_factory
def systemGetAll():
    authInfo = _getUcsAuthInfo((request.headers))
    handle = UcsHandle(*authInfo, secure=False)
    if handle.login():
        elements = [{"ciscoXmlName": "EquipmentChassis", "humanReadableName": "Chassis"},
                    {"ciscoXmlName": "NetworkElement", "humanReadableName": "Fabric Interconnects"},
                    {"ciscoXmlName": "EquipmentFex", "humanReadableName": "FEX"},
                    {"ciscoXmlName": "computeRackUnit", "humanReadableName": "Servers"}]
        finalObjs = {}
        for x in elements:
            units = []
            try:
                components = handle.query_children(in_dn="sys", class_id=x["ciscoXmlName"])
            except UcsException as e:
                handle.logout()
                return 'Internal Server Error', e.error_descr, 500
            else:
                if(type(components) == list):
                    for y in components:
                        subElement = {"relative_path": "/" + (vars(y))["dn"]}
                        units.append(subElement)
                    finalObjs[x["humanReadableName"]] = units
                    handle.logout()
                else:
                    handle.logout()
                    return "Couldn't fetch " + x["ciscoXmlName"], "", 500
        return finalObjs
    else:
        handle.logout()
        return 'Forbidden', "", 403


@http_body_factory
def getRackmount():
    authInfo = _getUcsAuthInfo((request.headers))
    data = []
    handle = UcsHandle(*authInfo, secure=False)
    if handle.login():
        try:
            computeRackUnit = handle.query_children(in_dn="sys", class_id="computeRackUnit")
        except UcsException as e:
            handle.logout()
            return 'Internal Server Error', e.error_descr, 500
        else:
            if (type(computeRackUnit) == list):
                for x in computeRackUnit:
                    server = {}
                    server["name"] = x.rn
                    server["path"] = x.dn
                    server["macs"] = []
                    try:
                        macs = handle.query_children(in_dn=x.dn, class_id='PciEquipSlot')
                    except UcsException as e:
                        handle.logout()
                        return 'Internal Server Error', e.error_descr, 500
                    for y in macs:
                        server["macs"].append(y.mac_left)
                        server["macs"].append(y.mac_right)
                    data.append(server)
                    handle.logout()
                return data
            else:
                handle.logout()
                return "Couldn't fetch computeRackUnits:", "", 500

    else:
        handle.logout()
        return 'Forbidden', "", 403


@http_body_factory
def getCatalog(identifier=None):
    authInfo = _getUcsAuthInfo((request.headers))
    data = []

    handle = UcsHandle(*authInfo, secure=False)
    if handle.login():
        try:
            elements = handle.query_children(in_dn=identifier)
        except UcsException as e:
            handle.logout()
            return 'Internal Server Error', e.error_descr, 500
        else:
            if (type(elements) == list):
                for element in elements:
                    data.append(reduce(element.__dict__))
                handle.logout()
                return data
            else:
                handle.logout()
                return "Couldn't fetch " + identifier, "", 500
    else:
        handle.logout()
        return 'Forbidden', "", 403


@http_body_factory
def getChassis():
    authInfo = _getUcsAuthInfo((request.headers))
    data = []
    handle = UcsHandle(*authInfo, secure=False)
    if handle.login():
        try:
            elememts = handle.query_children(in_dn="sys", class_id="EquipmentChassis")
        except UcsException as e:
            return 'Internal Server Error', e.error_descr, 500
        else:
            if (type(elememts) == list):
                for element in elememts:
                    chassis = {}
                    identifier = element.dn
                    obj = handle.query_dn(dn=identifier)
                    chassis["name"] = obj.rn
                    chassis["path"] = obj.dn
                    chassis["members"] = []
                    try:
                        blades = handle.query_children(in_dn=identifier, class_id='ComputeBlade')
                    except UcsException as e:
                        handle.logout()
                        return 'Internal Server Error', e.error_descr, 500
                    else:
                        if (type(blades) == list):
                            for x in blades:
                                server = {}
                                server["name"] = x.rn
                                server["path"] = x.dn
                                server["macs"] = []
                                try:
                                    adptares = handle.query_children(in_dn=x.dn, class_id='AdaptorUnit')
                                except UcsException as e:
                                    handle.logout()
                                    return 'Internal Server Error', e.error_descr, 500
                                else:
                                    for x in adptares:
                                        server["macs"].append(x.base_mac)
                                    chassis["members"].append(server)
                            data.append(chassis)
                        else:
                            handle.logout()
                            return "Couldn't fetch ComputeBlade", "", 500
            else:
                handle.logout()
                return "Couldn't fetch EquipmentChassis", "", 500
    else:
        handle.logout()
        return 'Forbidden', "", 403
    handle.logout()
    return data


@http_body_factory
def getServiceProfile():
    authInfo = _getUcsAuthInfo((request.headers))
    handle = UcsHandle(*authInfo, secure=False)
    if not handle.login():
        handle.logout()
        return 'Forbidden', "", 403
    rootElements = [{"ciscoXmlName": "orgOrg", "humanReadableName": "ServiceProfile"}]
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
                    lsList = handle.query_children(in_dn="org-root", class_id="lsServer")
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
def powerMgmt(identifier=None, action=None):
    authInfo = _getUcsAuthInfo((request.headers))
    handle = UcsHandle(*authInfo, secure=False)
    if handle.login():
        try:
            data = _service_profile_power_set(handle=handle, dn=identifier, state=action)
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
            " 'ipmi-reset', 'hard-reset-immediate', 'soft-shut-down' ".format(state))
    data = LsPower(
        parent_mo_or_dn=sp_mo,
        state=state)
    handle.set_mo(sp_mo)
    handle.commit()
    return data


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

    return(host, user, password)


def reduce(object):
    # remove the private propeties of an obj
    for property in object.keys():
        if (property[0] == "_"):
            del object[property]
    return object
