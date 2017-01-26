# Copyright 2017, Dell EMC, Inc.

from ucsmsdk.ucshandle import UcsHandle
import pickle

def login_get(host = None, user = None, password = None):
    handle = UcsHandle(host, user, password,secure=False);
    if handle.login():
        return handle.cookie;


def systemGetAll(host = None, user = None, password = None):
    handle = UcsHandle(host, user, password, secure=False)
    if handle.login():
        elements = [{"ciscoXmlName": "EquipmentChassis", "humanReadableName": "Chassis"},
                    {"ciscoXmlName": "NetworkElement", "humanReadableName": "Fabric Interconnects"},
                    {"ciscoXmlName": "EquipmentFex", "humanReadableName": "FEX"},
                    {"ciscoXmlName": "computeRackUnit", "humanReadableName": "Servers"}]
        finalObjs = {}
        for x in elements:
            units = []
            components = handle.query_children(in_dn="sys", class_id=x["ciscoXmlName"])
            for y in components:
                subElement = {"relative_path": "/"+(vars(y))["dn"]}
                units.append(subElement)
            finalObjs[x["humanReadableName"]]=units
            handle.logout()
        return finalObjs

def getRackmount(host = None, user = None, password = None):
    data = []
    handle = UcsHandle(host, user, password, secure=False)
    if handle.login():
        computeRackUnit = handle.query_children(in_dn="sys", class_id="computeRackUnit")
        for x in computeRackUnit:
            server={}
            server["name"]=x.rn
            server["path"]=x.dn
            server["macs"]=[]
            macs = handle.query_children(in_dn=x.dn, class_id='PciEquipSlot')
            for y in macs:
                server["macs"].append(y.mac_left)
                server["macs"].append(y.mac_right)
            data.append(server)
            handle.logout()
        return data

def getCatalog(host = None,  user = None, password = None, identifier=None):

    handle = UcsHandle(host, user, password, secure=False)
    if handle.login():
        element = handle.query_dn(dn=identifier)
        catalog = element.__dict__
        for property in catalog.keys():
            if(property[0]=="_"):
                del catalog[property]
        handle.logout()
        return catalog




