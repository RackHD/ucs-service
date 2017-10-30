#  Copyright 2017, Dell EMC, Inc.
import re
import time
from ucsmsdk.ucsexception import UcsException
from ucsmsdk.mometa.ls.LsPower import LsPowerConsts
from ucsmsdk.mometa.ls.LsPower import LsPower
from ucsmsdk.ucshandle import UcsHandle

SESSION_DURATION = 60


class Ucs:
    """Representation of UCS methods collection"""

    @staticmethod
    def login_get(headers):
        authInfo = Ucs._getUcsAuthInfo(headers)
        handle = UcsHandle(*authInfo, secure=False)
        if handle.login():
            return handle.cookie

    @staticmethod
    def systemGetAll(headers):
        authInfo = Ucs._getUcsAuthInfo(headers)
        handle = UcsHandle(*authInfo, secure=False)
        if handle.login():
            elements = [{
                "ciscoXmlName": "EquipmentChassis",
                "humanReadableName": "Chassis"
            }, {
                "ciscoXmlName": "NetworkElement",
                "humanReadableName": "Fabric Interconnects"
            }, {
                "ciscoXmlName": "EquipmentFex",
                "humanReadableName": "FEX"
            }, {
                "ciscoXmlName": "computeRackUnit",
                "humanReadableName": "Servers"
            }]
            finalObjs = {}
            for x in elements:
                units = []
                try:
                    components = handle.query_children(
                        in_dn="sys", class_id=x["ciscoXmlName"])
                except UcsException as e:
                    handle.logout()
                    return 'Internal Server Error', e.error_descr, 500
                else:
                    if (type(components) == list):
                        for y in components:
                            subElement = {
                                "relative_path": "/" + (vars(y))["dn"]
                            }
                            units.append(subElement)
                        finalObjs[x["humanReadableName"]] = units
                    else:
                        handle.logout()
                        return "Couldn't fetch " + x["ciscoXmlName"], "", 500
            handle.logout()
            return {"data": finalObjs}
        else:
            handle.logout()
            return {"error": "Forbidden"}

    @staticmethod
    def getRackmount(headers):
        authInfo = Ucs._getUcsAuthInfo(headers)
        data = []
        handle = UcsHandle(*authInfo, secure=False)
        if handle.login():
            try:
                computeRackUnit = handle.query_children(
                    in_dn="sys", class_id="computeRackUnit")
            except UcsException as e:
                handle.logout()
                raise e
            else:
                if (type(computeRackUnit) == list):
                    for x in computeRackUnit:
                        server = {}
                        server["name"] = x.rn
                        server["path"] = x.dn
                        server["macs"] = []
                        try:
                            macs = handle.query_children(
                                in_dn=x.dn, class_id='PciEquipSlot')
                        except UcsException as e:
                            handle.logout()
                            raise e
                        for y in macs:
                            server["macs"].append(y.mac_left)
                            server["macs"].append(y.mac_right)
                        data.append(server)
                    handle.logout()
                    return {"data": data}
                else:
                    handle.logout()
                    return {"error": "Couldn't fetch computeRackUnits"}

        else:
            handle.logout()
            return {"error": "Forbidden"}

    @staticmethod
    def getCatalog(headers, identifier=None):
        authInfo = Ucs._getUcsAuthInfo(headers)
        data = []

        handle = UcsHandle(*authInfo, secure=False)
        if handle.login():
            try:
                elements = (handle.query_children(in_dn=identifier))
                elements.append(handle.query_dn(dn=identifier))
                for element in elements:
                    if (element):
                        data.append(Ucs._reduce(element.__dict__))
                handle.logout()
                return {"data": data}
            except UcsException as e:
                handle.logout()
                raise e
        else:
            handle.logout()
            return {"error": "Forbidden"}

    @staticmethod
    def getPollers(headers, identifier, classIds, handlers=None):
        """
            Get node pollers data by given class ids
            @param identifier: dn string of a node
            @param classIds: a list of class ids to be retrieved
        """
        handle = Ucs._getHandler(headers, handlers)
        if not handle:
            return {"error": "Forbidden"}
        try:
            result = {}
            excludeBade = ''
            pattern = re.compile('^sys/chassis-\d{1,3}$')
            if pattern.match(identifier):
                excludeBade = ' and not (dn, ".*blade.*", type="re")'
            for class_id in classIds:
                filter_str = '(dn, "{}.*", type="re"){}'.format(identifier, excludeBade)
                items = handle.query_classid(class_id=class_id, filter_str=filter_str)
                colletion = []
                for item in items:
                    colletion.append(Ucs._reduce(item.__dict__))
                result[class_id] = colletion
            return {"data": result}
        except UcsException as e:
            handle.logout()
            raise e

    @staticmethod
    def getChassis(headers):
        authInfo = Ucs._getUcsAuthInfo(headers)
        data = []
        handle = UcsHandle(*authInfo, secure=False)
        if handle.login():
            try:
                elememts = handle.query_children(
                    in_dn="sys", class_id="EquipmentChassis")
            except UcsException as e:
                handle.logout()
                raise e
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
                            blades = handle.query_children(
                                in_dn=identifier, class_id='ComputeBlade')
                        except UcsException as e:
                            handle.logout()
                            raise e
                        else:
                            if (type(blades) == list):
                                for x in blades:
                                    server = {}
                                    server["name"] = x.rn
                                    server["path"] = x.dn
                                    server["macs"] = []
                                    try:
                                        adptares = handle.query_children(
                                            in_dn=x.dn, class_id='AdaptorUnit')
                                    except UcsException as e:
                                        handle.logout()
                                        raise e
                                    else:
                                        for x in adptares:
                                            server["macs"].append(x.base_mac)
                                        chassis["members"].append(server)
                                data.append(chassis)
                            else:
                                handle.logout()
                                return {"error": "Couldn't fetch ComputeBlade"}
                else:
                    handle.logout()
                    return {"error": "Couldn't fetch EquipmentChassis"}
        else:
            handle.logout()
            return {"error": "Forbidden"}
        handle.logout()
        return {"data": data}

    @staticmethod
    def getServiceProfile(headers):
        authInfo = Ucs._getUcsAuthInfo(headers)
        handle = UcsHandle(*authInfo, secure=False)
        if not handle.login():
            handle.logout()
            return {"error": "Forbidden"}
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
                raise e
            else:
                if not (type(components) == list):
                    handle.logout()
                    return {
                        "error": "Couldn't fetch " + x["humanReadableName"]
                    }

                for y in components:
                    subElement["org"] = y.level
                    subElement["members"] = []
                    try:
                        lsList = handle.query_children(
                            in_dn="org-root", class_id="lsServer")
                    except UcsException as e:
                        handle.logout()
                        raise e
                    else:
                        if not (type(lsList) == list):
                            handle.logout()
                            return {"error": "Couldn't fetch Logical Servers"}
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
        return {"data": finalObjs}

    @staticmethod
    def powerStatus(headers, identifier=None):
        authInfo = Ucs._getUcsAuthInfo(headers)
        handle = UcsHandle(*authInfo, secure=False)
        if handle.login():
            try:
                state = Ucs._powerStatus(identifier, handle)
            except UcsException as e:
                handle.logout()
                raise e
            else:
                handle.logout()
                return {"data": {"serverState": state}}
        else:
            handle.logout()
            return {"error": "Forbidden"}

    @staticmethod
    def powerMgmt(headers, identifier=None, action=None, physical=False):
        authInfo = Ucs._getUcsAuthInfo(headers)
        handle = UcsHandle(*authInfo, secure=False)
        if handle.login():
            try:
                if physical:
                    data = Ucs._physical_power_set(
                        handle=handle, dn=identifier, state=action)
                else:
                    data = Ucs._service_profile_power_set(
                        handle=handle, dn=identifier, state=action)
            except UcsException as e:
                handle.logout()
                raise e
            else:
                handle.logout()
                data = Ucs._reduce(data.__dict__)
            return {"data": data}
        else:
            handle.logout()
            return {"error": "Forbidden"}

    @staticmethod
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
                "'on', 'off', 'cycle-wait','cycle-immediate', "
                "'bmc-reset-immediate',"
                " 'ipmi-reset', 'hard-reset-immediate', 'soft-shut-down' ".
                format(state))
        data = LsPower(parent_mo_or_dn=sp_mo, state=state)
        handle.set_mo(sp_mo)
        handle.commit()
        return data

    @staticmethod
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
            raise UcsException(
                "physical_power_set: Failed to set element power",
                "sever %s does not exist" % (dn))
        elif (mo._class_id == "LsServer" and mo.assigned_to_dn is not None and
              mo.assigned_to_dn != ""):
            server_mo = handle.query_dn(mo.assigned_to_dn)
        elif (mo._class_id == "ComputeRackUnit" or
              mo._class_id == "compuetBlade"):
            server_mo = mo
        else:
            raise UcsException(
                "physical_power_set: Failed to set element power",
                "sever %s has an unknown class_id %s" % (dn, mo._class_id))
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
                "action '{0}' is not valid."
                " physical power control supports states: "
                "'off', 'on', 'cycle-wait', 'cycle-immediate', "
                "bmc-reset-immediate, "
                "'bmc-reset-wait', 'hard-reset-immediate', 'hard-reset-wait',"
                "'ipmi-reset',"
                "'cmos-reset-immediate', 'diagnostic-interrupt',"
                "'kvm-reset', 'policy' ".format(state))

        server_mo.admin_power = state
        handle.set_mo(server_mo)
        handle.commit()
        return server_mo

    @staticmethod
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

    @staticmethod
    def _getUcsAuthInfo(headers):
        host = headers.get('ucs-host')
        user = headers.get('ucs-user')
        password = headers.get('ucs-password')

        return (host, user, password)

    @staticmethod
    def _reduce(object):
        # remove the private propeties of an obj
        for property in object.keys():
            if (property[0] == "_"):
                del object[property]
        return object

    @staticmethod
    def _getHandler(headers, handlers):
        authInfo = Ucs._getUcsAuthInfo(headers)
        host, user, password = authInfo
        timestamp = time.time()
        handle_obj = handlers.get(host, None)
        ucs_handle = handle_obj and handle_obj.get('ucs-handle', None)
        is_auth_valid = ucs_handle \
            and handle_obj.get('ucs-user') == user \
            and handle_obj.get('ucs-password') == password \
            and (timestamp - handle_obj['timestamp']) < SESSION_DURATION
        if is_auth_valid:
            handle_obj['timestamp'] = timestamp
        else:
            if ucs_handle:
                # logout existing handler if it is invalid
                ucs_handle.logout()
            ucs_handle = UcsHandle(*authInfo, secure=False)
            if ucs_handle.login():
                ucs_handle_obj = {
                    'ucs-user': user,
                    'ucs-password': password,
                    'ucs-host': host,
                    'ucs-handle': ucs_handle,
                    'timestamp': timestamp
                }
                handlers[host] = ucs_handle_obj
            else:
                ucs_handle.logout()
                return None
        return ucs_handle
