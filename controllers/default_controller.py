# Copyright 2017, Dell EMC, Inc.

from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsexception import UcsException


def login_get(host=None, user=None, password=None):
    handle = UcsHandle(host, user, password, secure=False)
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
def systemGetAll(host=None, user=None, password=None):
    handle = UcsHandle(host, user, password, secure=False)
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
                return 'Inrternal Server Error', e.error_descr, 500
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
        return 'Forbiden', "", 403


@http_body_factory
def getRackmount(host=None, user=None, password=None):
    data = []
    handle = UcsHandle(host, user, password, secure=False)
    if handle.login():
        try:
            computeRackUnit = handle.query_children(in_dn="sys", class_id="computeRackUnit")
        except UcsException as e:
            handle.logout()
            return 'Inrternal Server Error', e.error_descr, 500
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
                        return 'Inrternal Server Error', e.error_descr, 500
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
        return 'Forbiden', "", 403


@http_body_factory
def getCatalog(host=None, user=None, password=None, identifier=None):
    data = []

    handle = UcsHandle(host, user, password, secure=False)
    if handle.login():
        try:
            elements = handle.query_children(in_dn=identifier)
        except UcsException as e:
            handle.logout()
            return 'Inrternal Server Error', e.error_descr, 500
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
        return 'Forbiden', "", 403


@http_body_factory
def getChassis(host=None, user=None, password=None):
    data = []

    handle = UcsHandle(host, user, password, secure=False)
    if handle.login():
        try:
            elememts = handle.query_children(in_dn="sys", class_id="EquipmentChassis")
        except UcsException as e:
            return 'Inrternal Server Error', e.error_descr, 500
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
                        return 'Inrternal Server Error', e.error_descr, 500
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
                                    return 'Inrternal Server Error', e.error_descr, 500
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
        return 'Forbiden', "", 403
    handle.logout()
    return data


def reduce(object):
    # remove the private propeties of an obj
    for property in object.keys():
        if (property[0] == "_"):
            del object[property]
    return object
