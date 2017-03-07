# Copyright 2017, Dell EMC, Inc.

import unittest
import controllers.default_controller as controler
import mock

EXPECTED_COOKIE = 'chocolate chip'
HOST = 'hostname'
USER = 'somebody'
PASS = 'secret'
MOCK_DATA = 'data'
MOCK_ID = 'sys/rack1'
MOCK_ID_RACKMOUNT = "sys/rack-unit-7"
MOCK_ID_MACS = "PciEquipSlot"
MOCK_ID_CHASSIS = "sys/chassis-6"
MOCK_ID_COMPUTEBLADE = "sys/chassis-6/blade-1"
MOCK_ID_ADATORUNIT = "sys/chassis-6/blade-1/adaptor-1"
MOCK_ID_SERVICEPROFILE = "root"
MOCK_ID_LOGICALSERVER = "org-root/ls-Profile3"
MOCK_ID_LOGICALSERVER_MEMBER = {
    'assoc_state': 'associated',
    'dn': 'org-root/ls-Profile3',
    'pn_dn': 'sys/rack-unit-3',
    'rn': 'org-root/ls-Profile3'
}


class test_default_controller(unittest.TestCase):

    def setUp(self):
        print "running setup"

    def tearDown(self):
        print "running teardown"

    @mock.patch('controllers.default_controller.UcsHandle')
    def testLoginSuccess(self, mock_ucs):
        print "running test"
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.cookie = EXPECTED_COOKIE
        cookie = controler.login_get(HOST, USER, PASS)
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        self.assertEqual(cookie, EXPECTED_COOKIE, 'returned cookie %s does not equal %s' % (cookie, EXPECTED_COOKIE))

    @mock.patch('controllers.default_controller.UcsHandle')
    def testLoginFailure(self, mock_ucs):
        print "running test"
        mock_ucs.return_value.login.return_value = False
        mock_ucs.return_value.cookie = EXPECTED_COOKIE
        cookie = controler.login_get(HOST, USER, PASS)
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
        def __init__(self, dn, class_id):
            self.dn = dn
            self._class_id = class_id

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetRackmountSuccess(self, mock_ucs):
        left_mac = "00:00:FF:38:64:00"
        right_mac = "00:00:FF:38:64:01"
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = \
            [[self.mockRackmountClass(data=MOCK_ID_RACKMOUNT)], [self.mockPciEquipSlot(left_mac, right_mac)]]
        # call getRackmount
        result = controler.getRackmount(HOST, USER, PASS)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        calls = [mock.call(class_id='computeRackUnit', in_dn='sys'),
                 mock.call(class_id=MOCK_ID_MACS, in_dn=MOCK_ID_RACKMOUNT)]
        mock_ucs.return_value.query_children.assert_has_calls(calls)
        mock_ucs.return_value.logout.assert_called_once()
        # verify return data
        di = {
            'macs': [left_mac, right_mac],
            'name': MOCK_ID_RACKMOUNT,
            'path': MOCK_ID_RACKMOUNT
        }
        self.assertEqual(di, result[0], 'result does not contain member "data"')

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetRackmounForbidden(self, mock_ucs):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = False
        # call getCaltalog
        result = controler.getRackmount(HOST, USER, PASS)
        # verify UCS Mocks were not called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.query_dn.assert_not_called()
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetRackmounInternalServerError(self, mock_ucs):
        """Invoke a 500 http error"""
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = [""]
        # call getCaltalog
        result = controler.getRackmount(HOST, USER, PASS)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        # verify return data
        self.assertEqual(result, ({'message': "Couldn't fetch computeRackUnits:", 'stack': '', 'status': 500}, 500))

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetCatalogSuccess(self, mock_ucs):
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = [[self.mockCatalogClass(data=MOCK_DATA)]]
        # call getCaltalog
        result = controler.getCatalog(HOST, USER, PASS, identifier=MOCK_ID)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        calls = [mock.call(in_dn=MOCK_ID)]
        mock_ucs.return_value.query_children.assert_has_calls(calls)
        mock_ucs.return_value.logout.assert_called_once()
        # verify return data
        self.assertIn({'data': 'data'}, result, 'result does not contain member "data"')
        self.assertEqual(MOCK_DATA, result[0]['data'], 'result["data"] does not equal "{}"'.format(MOCK_DATA))
        self.assertNotIn('_privData', result, 'result contains private member "_privData"')\


    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetCatalogForbiden(self, mock_ucs):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = False
        # call getCaltalog
        result = controler.getCatalog(HOST, USER, PASS, identifier=MOCK_ID)
        # verify UCS Mocks were not called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.query_dn.assert_not_called()
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetCatalogInternalServerError(self, mock_ucs):
        """Invoke a 500 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = [""]
        # call getCaltalog
        result = controler.getCatalog(HOST, USER, PASS, identifier=MOCK_ID)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        calls = [mock.call(in_dn=MOCK_ID)]
        mock_ucs.return_value.query_children.assert_has_calls(calls)
        # verify return data
        self.assertEqual(result, ({'message': "Couldn't fetch sys/rack1", 'stack': '', 'status': 500}, 500))

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetChassisSuccess(self, mock_ucs):
        mac = '00:00:FF:FF:32:02'
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = \
            [[self.mockChassisClass(data=MOCK_ID_CHASSIS)],
             [self.mockComputeBlade(data=MOCK_ID_COMPUTEBLADE)],
             [self.mockAaptorUnit(MOCK_ID_ADATORUNIT, mac)]]
        # call getChassis
        result = controler.getChassis(HOST, USER, PASS)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.logout.assert_called_once()
        # verify return data
        di = {
            'macs': [mac],
            'name': MOCK_ID_COMPUTEBLADE,
            'path': MOCK_ID_COMPUTEBLADE
        }
        self.assertEqual(di, result[0]["members"][0], "Unexpected Chassis Data")

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetChassisForbiden(self, mock_ucs):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = False
        # call getChassis
        result = controler.getChassis(HOST, USER, PASS)
        # verify UCS Mocks were not called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.query_dn.assert_not_called()
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetChassisInternalServerError(self, mock_ucs):
        """Invoke a 500 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = ["", "", ""]
        # call getChassis
        result = controler.getChassis(HOST, USER, PASS)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        # verify return data
        self.assertEqual(result, ({'status': 500, 'message': "Couldn't fetch EquipmentChassis", 'stack': ''}, 500))

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetServiceProfileSuccess(self, mock_ucs):
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
        # call getServiceProfile
        result = controler.getServiceProfile(HOST, USER, PASS)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.logout.assert_called_once()
        # verify return data
        di = {
            'name': MOCK_ID_LOGICALSERVER,
            'path': MOCK_ID_LOGICALSERVER,
            'associatedServer': serverData,
            'assoc_state': state
        }
        self.assertEqual(di, result['ServiceProfile']['members'][0], "Unexpected Chassis Data")

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetServiceProfileForbiden(self, mock_ucs):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = False
        # call getServiceProfile
        result = controler.getServiceProfile(HOST, USER, PASS)
        # verify UCS Mocks were not called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.query_dn.assert_not_called()
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetServiceProfileInternalServerError(self, mock_ucs):
        """Invoke a 500 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = [""]
        # call getServiceProfile
        result = controler.getServiceProfile(HOST, USER, PASS)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        # verify return data
        self.assertEqual(result, ({'status': 500, 'message': "Couldn't fetch ServiceProfile", 'stack': ''}, 500))

    @mock.patch('controllers.default_controller.LsPowerConsts')
    @mock.patch('controllers.default_controller.LsPower')
    @mock.patch('controllers.default_controller.UcsHandle')
    def testPowerSuccess(self, mock_ucs, mock_LsPower_Consts, mock_LsPower):
        # setup UCS mocks
        mock_LsPower_Consts.return_value.STATE_DOWN.return_value = True
        mock_LsPower.return_value.return_value = True
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_dn.side_effect = \
            [self.mockBlade("Non_LsServer", "sys/chassis-3/blade-3", "org-root/ls-ps1"),
             self.mockServiceProfile("org-root/ls-ps1", "LsServer"), ""]
        # call powerMgmt
        controler.powerMgmt(HOST, USER, PASS, "sys/chassis-3/blade-3", "off")
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.logout.assert_called_once()
        assert mock_ucs.return_value.query_dn.call_count == 2
        # assert that the appropriate service profile constant has been set
        assert mock_LsPower_Consts.STATE_DOWN is not None

    @mock.patch('controllers.default_controller.UcsHandle')
    def testPowerInternalServerError_1(self, mock_ucs):
        """Invoke a 500 http error by sending an invalid power operation 'off3'"""
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_dn.side_effect = \
            [self.mockBlade("Non_LsServer", "sys/chassis-3/blade-3", "org-root/ls-ps1"),
             self.mockServiceProfile("org-root/ls-ps1", "LsServer"), ""]
        # call powerMgmt
        result = controler.powerMgmt(HOST, USER, PASS, "sys/chassis-3/blade-3", "off3")
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.logout.assert_called_once()
        assert mock_ucs.return_value.query_dn.call_count == 2
        di = ({'status': 500, 'message': 'Internal Server Error',
               'stack': "action %s is not valid. Choose one of the following: 'on', 'off', 'cycle-wait'or 'cycle-immediate'"},
              500)
        self.assertEqual(di, result, "Unexpected exception Data")

    @mock.patch('controllers.default_controller.UcsHandle')
    def testPowerInternalServerError_2(self, mock_ucs):
        """Invoke a 500 http error by sending an invalid dn"""
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_dn.side_effect = \
            [None,
             "", ""]
        # call powerMgmt
        result = controler.powerMgmt(HOST, USER, PASS, "sys/chassis-3/blade-3", "off")
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.logout.assert_called_once()
        assert mock_ucs.return_value.query_dn.call_count == 1
        di = ({'status': 500, 'message': 'Internal Server Error', 'stack': 'sever sys/chassis-3/blade-3 does not exist'}, 500)
        self.assertEqual(di, result, "Unexpected exception Data")

    @mock.patch('controllers.default_controller.UcsHandle')
    def testPowerInternalServerError_3(self, mock_ucs):
        """Invoke a 500 http error by not associating a server to a service profile"""
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_dn.side_effect = \
            [self.mockBlade("Non_LsServer", "sys/chassis-3/blade-3", ""),
             self.mockServiceProfile("org-root/ls-ps1", "LsServer"), ""]
        # call powerMgmt
        result = controler.powerMgmt(HOST, USER, PASS, "sys/chassis-3/blade-3", "off")
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.logout.assert_called_once()
        # assert mock_ucs.return_value.query_dn.call_count == 2
        di = ({'status': 500, 'message': 'Internal Server Error',
               'stack': 'sever sys/chassis-3/blade-3 is not associated to a service profile'}, 500)
        self.assertEqual(di, result, "Unexpected exception Data")

    @mock.patch('controllers.default_controller.UcsHandle')
    def testPowerMgmtForbiden(self, mock_ucs):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = False
        # call powerMgmt
        result = controler.powerMgmt(HOST, USER, PASS, identifier=MOCK_ID)
        # verify UCS Mocks were not called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.query_dn.assert_not_called()
        self.assertEqual(result, ({'status': 403, 'message': 'Forbidden', 'stack': ''}, 403))
