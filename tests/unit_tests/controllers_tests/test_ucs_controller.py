# Copyright 2017, Dell EMC, Inc.

import unittest
import mock
import controllers.ucs_controller as controler
from ucsmsdk.ucsexception import UcsException

EXPECTED_COOKIE = 'chocolate chip'
HOST = 'hostname'
USER = 'somebody'
PASS = 'secret'
MOCK_HEADER = {
    'ucs-host': HOST,
    'ucs-password': PASS,
    'ucs-user': USER
}
MOCK_DATA = 'data'
MOCK_ID = 'sys/rack1'
MOCK_ID_RACKMOUNT = "sys/rack-unit-7"
MOCK_ID_CHASSIS = "sys/chassis-6"
MOCK_ID_MACS = "PciEquipSlot"
MOCK_MAC = "00:11:22:33:44:55"
MOCK_MAC_2 = "11:22:33:44:55:66"
MOCK_ID_COMPUTEBLADE = "sys/chassis-6/blade-1"
MOCK_ID_COMPUTEBLADE_2 = "sys/chassis-6/blade-2"
MOCK_ID_ADAPTORUNIT = "sys/chassis-6/blade-1/adaptor-1"
MOCK_ID_ADAPTORUNIT_2 = "sys/chassis-6/blade-2/adaptor-1"
MOCK_ID_SERVICEPROFILE = "root"
MOCK_ID_LOGICALSERVER = "org-root/ls-Profile3"
MOCK_ID_LOGICALSERVER_MEMBER = {
    'assoc_state': 'associated',
    'dn': 'org-root/ls-Profile3',
    'pn_dn': 'sys/rack-unit-3',
    'rn': 'org-root/ls-Profile3'
}
MOCK_CLASS_IDS = ['processorEnvStats', 'memoryUnitEnvStats']
MOCK_CLASS_ID_DATA = ['CPU', 'Mem']


class test_default_controller(unittest.TestCase):

    def setUp(self):
        print "running controller tests setup"

    def tearDown(self):
        print "running controller tests tear down"

    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('service.ucs.UcsHandle')
    def testLoginSuccess(self, mock_ucs, mock_request):
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.cookie = EXPECTED_COOKIE
        mock_request.headers = MOCK_HEADER
        cookie = controler.login_get()
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        self.assertEqual(cookie, EXPECTED_COOKIE, 'returned cookie %s does not equal %s' % (cookie, EXPECTED_COOKIE))

    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('service.ucs.UcsHandle')
    def testLoginFailure(self, mock_ucs, mock_request):
        mock_ucs.return_value.login.return_value = False
        mock_ucs.return_value.cookie = EXPECTED_COOKIE
        mock_request.headers = MOCK_HEADER
        cookie = controler.login_get()
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        self.assertIsNone(cookie, 'returned cookie does not equal None')

    class mockCatalogClass:
        def __init__(self, data):
            self._privData = "private 1"
            self.data = data

    class mockRackmountClass:
        def __init__(self, data):
            self.dn = data
            self.rn = data
            self.serial = "RK38"

    class mockPciEquipSlot:
        def __init__(self, l, r):
            self.mac_left = l
            self.mac_right = r

    class mockChassisClass:
        def __init__(self, data):
            self.dn = data

    class mockComputeBlade:
        def __init__(self, data):
            self.dn = data
            self.rn = data

    class mockAaptorUnit:
        def __init__(self, id, mac):
            self.dn = id
            self.rn = id
            self.base_mac = mac

    class mockServiceProfileClass:
        def __init__(self, data):
            self.level = data

    class mocklsServer:
        def __init__(self, data):
            self.dn = data

    class mocklsServerMembers:
        def __init__(self, data):
            self.dn = data['dn']
            self.rn = data['rn']
            self.pn_dn = data['pn_dn']
            self.assoc_state = data['assoc_state']

    class mockBlade:
        def __init__(self, class_id, dn, assigned_to_dn):
            self._class_id = class_id
            self.dn = dn
            self.assigned_to_dn = assigned_to_dn

    class mockServiceProfile:
        def __init__(self, dn, class_id, state=None):
            self.dn = dn
            self._class_id = class_id

    class mockManagedObject:
        def __init__(self, dn, class_id, admin_power='policy'):
            self.dn = dn
            self._class_id = class_id
            self.admin_power = admin_power

    class mockCurrentApp:
        config = None

        def __init__(self, data):
            self.config = {"handlers": data}

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetRackmountSuccess(self, mock_ucs, mock_request, mock_current_app):
        left_mac = "00:00:FF:38:64:00"
        right_mac = "00:00:FF:38:64:01"
        # setup UCS mocks
        mock_ucs.return_value.query_children.side_effect = \
            [[self.mockRackmountClass(data=MOCK_ID_RACKMOUNT)], [self.mockPciEquipSlot(left_mac, right_mac)]]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything")
        # call getRackmount
        result = controler.getRackmount()
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        calls = [mock.call(class_id='computeRackUnit', in_dn='sys'),
                 mock.call(class_id=MOCK_ID_MACS, in_dn=MOCK_ID_RACKMOUNT)]
        mock_ucs.return_value.query_children.assert_has_calls(calls)
        # verify return data
        di = {
            'macs': [left_mac, right_mac],
            'name': MOCK_ID_RACKMOUNT,
            'path': MOCK_ID_RACKMOUNT
        }
        self.assertEqual(di, result[0][0], 'result does not contain member "data"')

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetRackmounForbidden(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value = None
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything")
        # call getCaltalog
        result = controler.getRackmount()
        # verify UCS Mocks were not called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetRackmounInternalServerError(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 500 http error"""
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = [""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything")
        # call getCaltalog
        result = controler.getRackmount()
        # verify UCS Mocks were called
        self.assertEqual(result, ({'message': "Couldn't fetch computeRackUnits", 'stack': '', 'status': 500}, 500))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetCatalogSuccess(self, mock_ucs, mock_request, mock_current_app):
        # setup UCS mocks
        mock_ucs.return_value.query_children.side_effect = [[self.mockCatalogClass(data=MOCK_DATA)]]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call getCaltalog
        result = controler.getCatalog(identifier=MOCK_ID)
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        calls = [mock.call(in_dn=MOCK_ID)]
        mock_ucs.return_value.query_children.assert_has_calls(calls)
        # verify return data
        self.assertIn({'data': 'data'}, result[0], 'result does not contain member "data"')
        self.assertEqual(MOCK_DATA, result[0][0]['data'], 'result["data"] does not equal "{}"'.format(MOCK_DATA))
        self.assertNotIn('_privData', result[0], 'result contains private member "_privData"')\


    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetCatalogForbiden(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value = None
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything")
        # call getCaltalog
        result = controler.getCatalog(identifier=MOCK_ID)
        # verify UCS Mocks were not called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('service.ucs.UcsHandle')
    def testGetCatalogInternalServerError(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 500 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = [[]]
        mock_ucs.return_value.query_dn.side_effect = UcsException(500, "Mock Server Error")
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config

        mock_request.headers = MOCK_HEADER
        # call getCaltalog
        result = controler.getCatalog(identifier=MOCK_ID)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        calls = [mock.call(in_dn=MOCK_ID)]
        mock_ucs.return_value.query_children.assert_has_calls(calls)
        calls = [mock.call(dn=MOCK_ID)]
        mock_ucs.return_value.query_dn.assert_has_calls(calls)

        # verify return data
        self.assertEqual(result, ({'message': "Internal Server Error", 'stack': 'Mock Server Error', 'status': 500}, 500))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetChassisSuccess(self, mock_ucs, mock_request, mock_current_app):
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = \
            [[self.mockChassisClass(data=MOCK_ID_CHASSIS)],
             [self.mockComputeBlade(data=MOCK_ID_COMPUTEBLADE), self.mockComputeBlade(data=MOCK_ID_COMPUTEBLADE_2)],
             [self.mockAaptorUnit(MOCK_ID_ADAPTORUNIT, MOCK_MAC)],
             [self.mockAaptorUnit(MOCK_ID_ADAPTORUNIT_2, MOCK_MAC_2)]]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call getChassis
        result = controler.getChassis()
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        # verify return data
        di = \
            [
                {
                    'macs': [MOCK_MAC],
                    'name': MOCK_ID_COMPUTEBLADE,
                    'path': MOCK_ID_COMPUTEBLADE
                },
                {
                    'macs': [MOCK_MAC_2],
                    'name': MOCK_ID_COMPUTEBLADE_2,
                    'path': MOCK_ID_COMPUTEBLADE_2
                }
            ]
        self.assertEqual(1, len(result[0]), "expected 1 chassis, got {}".format(len(result)))
        self.assertEqual(di, result[0][0]["members"], "Unexpected Chassis Data")

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetChassisForbiden(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value = None
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call getChassis
        result = controler.getChassis()
        # verify UCS Mocks were not called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetChassisInternalServerError(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 500 http error"""
        # setup UCS mocks
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = ["", "", ""]
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        mock_request.headers = MOCK_HEADER
        # call getChassis
        result = controler.getChassis()
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        # verify return data
        self.assertEqual(result, ({'status': 500, 'message': "Couldn't fetch EquipmentChassis", 'stack': ''}, 500))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetServiceProfileSuccess(self, mock_ucs, mock_request, mock_current_app):
        serverData = "sys/rack-unit-3"
        state = "associated"
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_classid.side_effect = \
            [[self.mockServiceProfileClass(data=MOCK_ID_SERVICEPROFILE)]
             ]
        mock_ucs.return_value.query_children.side_effect = \
            [[self.mocklsServer(data=MOCK_ID_LOGICALSERVER)]
             ]
        mock_ucs.return_value.query_dn.side_effect = \
            [self.mocklsServerMembers(data=MOCK_ID_LOGICALSERVER_MEMBER)]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call getServiceProfile
        result = controler.getServiceProfile()
        # verify return data
        di = {
            'name': MOCK_ID_LOGICALSERVER,
            'path': MOCK_ID_LOGICALSERVER,
            'associatedServer': serverData,
            'assoc_state': state
        }
        self.assertEqual(di, result[0]['ServiceProfile']['members'][0], "Unexpected Chassis Data")

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetServiceProfileForbiden(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value = None
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call getServiceProfile
        result = controler.getServiceProfile()
        # verify UCS Mocks were not called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testGetServiceProfileInternalServerError(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 500 http error"""
        # setup UCS mocks
        mock_ucs.return_value.query_children.side_effect = [""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call getServiceProfile
        result = controler.getServiceProfile()
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        # verify return data
        self.assertEqual(result, ({'status': 500, 'message': "Couldn't fetch ServiceProfile", 'stack': ''}, 500))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('service.ucs.LsPower')
    @mock.patch('service.ucs.LsPowerConsts')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerSuccess(self, mock_ucs, mock_request, mock_LsPower_Consts, mock_LsPower, mock_current_app):
        # setup UCS mocks
        mock_LsPower_Consts.return_value.STATE_DOWN.return_value = True
        mock_LsPower.return_value.return_value = True
        mock_ucs.return_value.query_dn.side_effect = \
            [self.mockBlade("Non_LsServer", "sys/chassis-3/blade-3", "org-root/ls-ps1"),
             self.mockServiceProfile("org-root/ls-ps1", "LsServer"), ""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call powerMgmt
        controler.powerMgmt("sys/chassis-3/blade-3", "off")
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        assert mock_ucs.return_value.query_dn.call_count == 2
        # assert that the appropriate service profile constant has been set
        assert mock_LsPower_Consts.STATE_DOWN is not None

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerInternalServerError_1(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 500 http error by sending an invalid power operation 'off3'"""
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_dn.side_effect = \
            [self.mockBlade("Non_LsServer", "sys/chassis-3/blade-3", "org-root/ls-ps1"),
             self.mockServiceProfile("org-root/ls-ps1", "LsServer"), ""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call powerMgmt
        result = controler.powerMgmt("sys/chassis-3/blade-3", "off3")
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        mock_ucs.return_value.logout.assert_called_once()
        assert mock_ucs.return_value.query_dn.call_count == 2
        di = ({'status': 500, 'message': 'Internal Server Error',
               'stack': "action 'off3' is not valid. Choose one of the following: "
                        "'on', 'off', 'cycle-wait','cycle-immediate', 'bmc-reset-immediate', "
                        "'ipmi-reset', 'hard-reset-immediate', 'soft-shut-down' "}, 500)
        self.assertEqual(di, result, "Unexpected exception Data")

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerInternalServerError_2(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 500 http error by sending an invalid dn"""
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_dn.side_effect = \
            [None,
             "", ""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call powerMgmt
        result = controler.powerMgmt("sys/chassis-3/blade-3", "off")
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        mock_ucs.return_value.logout.assert_called_once()
        assert mock_ucs.return_value.query_dn.call_count == 1
        di = ({'status': 500, 'message': 'Internal Server Error', 'stack': 'sever sys/chassis-3/blade-3 does not exist'}, 500)
        self.assertEqual(di, result, "Unexpected exception Data")

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerInternalServerError_3(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 500 http error by not associating a server to a service profile"""
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_dn.side_effect = \
            [self.mockBlade("Non_LsServer", "sys/chassis-3/blade-3", ""),
             self.mockServiceProfile("org-root/ls-ps1", "LsServer"), ""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call powerMgmt
        result = controler.powerMgmt("sys/chassis-3/blade-3", "off")
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        mock_ucs.return_value.logout.assert_called_once()
        # assert mock_ucs.return_value.query_dn.call_count == 2
        di = ({'status': 500, 'message': 'Internal Server Error',
               'stack': 'sever sys/chassis-3/blade-3 is not associated to a service profile'}, 500)
        self.assertEqual(di, result, "Unexpected exception Data")

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerMgmtForbiden(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value = None
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call powerMgmt
        result = controler.powerMgmt(identifier=MOCK_ID)
        # verify UCS Mocks were not called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('service.ucs.LsPower')
    @mock.patch('service.ucs.LsPowerConsts')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerStatusSuccess(self, mock_ucs, mock_request, mock_LsPower_Consts, mock_LsPower, mock_current_app):
        # setup UCS mocks
        mock_LsPower_Consts.return_value.state.return_value = True
        mock_LsPower.return_value.return_value = "off"
        mock_ucs.return_value.query_dn.side_effect = \
            [self.mockBlade("Non_LsServer", "sys/chassis-3/blade-3", "org-root/ls-ps1"),
             self.mockServiceProfile("org-root/ls-ps1", "LsServer"), ""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        # call powerMgmt
        controler.powerStatus("sys/chassis-3/blade-3")
        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        assert mock_ucs.return_value.query_dn.call_count == 2
        # assert that the appropriate service profile constant has been set
        assert mock_LsPower_Consts.state.value is not "off"

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerStatusForbiden(self, mock_ucs, mock_request, mock_current_app):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value = None
        mock_request.headers = MOCK_HEADER
        # call powerMgmt
        result = controler.powerStatus(identifier=MOCK_ID)
        # verify UCS Mocks were not called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerPhysicalSuccess(self, mock_ucs, mock_request, mock_current_app):
        # setup UCS mocks
        mockBlade = self.mockBlade("LsServer", "ls-Chassis3Blade3", "sys/chassis-3/blade-3")
        mockMo = self.mockManagedObject("org-root/ls-ps1", "LsServer")
        mock_ucs.return_value.query_dn.side_effect = [mockBlade, mockMo, ""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config

        # call powerMgmt
        controler.powerMgmt("ls-Chassis3Blade3", "off", True)

        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        self.assertEqual(mock_ucs.return_value.query_dn.call_count, 2)
        calls = [mock.call("ls-Chassis3Blade3"), mock.call("sys/chassis-3/blade-3")]
        mock_ucs.return_value.query_dn.assert_has_calls(calls)
        calls = [mock.call(mockMo)]
        mock_ucs.return_value.set_mo.assert_has_calls(calls)
        self.assertEqual(mockMo.admin_power, "admin-down")
        mock_ucs.return_value.commit.assert_called_once()

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerPhysicalSuccess2(self, mock_ucs, mock_request, mock_current_app):
        # setup UCS mocks
        mockMo = self.mockManagedObject("sys/chassis-3/blade-3", "compuetBlade")
        mock_ucs.return_value.query_dn.side_effect = [mockMo, ""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config

        # call powerMgmt
        controler.powerMgmt("sys/chassis-3/blade-3", "off", True)

        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        self.assertEqual(mock_ucs.return_value.query_dn.call_count, 1)
        calls = [mock.call("sys/chassis-3/blade-3")]
        mock_ucs.return_value.query_dn.assert_has_calls(calls)
        calls = [mock.call(mockMo)]
        mock_ucs.return_value.set_mo.assert_has_calls(calls)
        self.assertEqual(mockMo.admin_power, "admin-down")
        mock_ucs.return_value.commit.assert_called_once()

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.request')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    def testPowerPhysicalFailure(self, mock_ucs, mock_request, mock_current_app):
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mockMo = self.mockManagedObject("sys/chassis-3/blade-3", "compuetBlade")
        mock_ucs.return_value.query_dn.side_effect = [mockMo, ""]
        mock_request.headers = MOCK_HEADER
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config

        # call powerMgmt
        result = controler.powerMgmt("sys/chassis-3/blade-3", "foo", True)

        # verify UCS Mocks were called
        headers = {'ucs-user': USER, 'ucs-host': HOST, 'ucs-password': PASS}
        mock_ucs.assert_called_with(headers, mock_current_app.config.get("handlers"))
        mock_ucs.return_value.logout.assert_called_once()
        self.assertEqual(mock_ucs.return_value.query_dn.call_count, 1)
        calls = [mock.call("sys/chassis-3/blade-3")]
        mock_ucs.return_value.query_dn.assert_has_calls(calls)
        self.assertEqual(result[0]['status'], 500, "expected status 500")

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    @mock.patch('controllers.ucs_controller.request')
    def testGetPollersSuccess(self, mock_request, mock_getHandler, mock_current_app):
        """Get Pollers Successfully"""
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything").config
        mock_getHandler.return_value.query_classid.side_effect = [
            [self.mockCatalogClass(data=MOCK_CLASS_ID_DATA[0])],
            [self.mockCatalogClass(data=MOCK_CLASS_ID_DATA[1])]
        ]
        mock_request.headers = MOCK_HEADER
        result = controler.getPollers(identifier=MOCK_ID, classIds=MOCK_CLASS_IDS)
        calls = []
        for i in range(2):
            mocked_class_id = MOCK_CLASS_IDS[i]
            mocked_filter_str = '(dn, "{}.*", type="re")'.format(MOCK_ID)
            mocked_call = mock.call(class_id=mocked_class_id, filter_str=mocked_filter_str)
            calls.append(mocked_call)
            self.assertEqual(MOCK_CLASS_ID_DATA[i], result[0][mocked_class_id][0]['data'],
                             'CPU data in result does not equal "{}"'.format(MOCK_CLASS_ID_DATA[i]))
        mock_getHandler.return_value.query_classid.assert_has_calls(calls)

    @mock.patch('controllers.ucs_controller.current_app')
    @mock.patch('controllers.ucs_controller.Ucs._getHandler')
    @mock.patch('controllers.ucs_controller.request')
    def testGetPollersForbiden(self, mock_request, mock_getHandler, mock_current_app):
        """Invoke a 403 http error"""
        mock_current_app.config.get.return_value = self.mockCurrentApp("Anything")
        mock_getHandler.return_value = None
        mock_request.headers = MOCK_HEADER
        result = controler.getPollers(identifier=MOCK_ID, classIds=MOCK_CLASS_IDS)
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))
