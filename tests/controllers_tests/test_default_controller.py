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
    def testGetRackmounForbiden(self, mock_ucs):
        """Invoke a 403 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = False
        # call getCaltalog
        result = controler.getRackmount(HOST, USER, PASS)
        # verify UCS Mocks were not called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.query_dn.assert_not_called()
        self.assertEqual(result, ({'status': 403, 'message': 'Forbiden', 'stack': ''}, 403))

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
        self.assertEqual(result, ({'status': 403, 'message': 'Forbiden', 'stack': ''}, 403))

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
        # call getCaltalog
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
        # call getCaltalog
        result = controler.getChassis(HOST, USER, PASS)
        # verify UCS Mocks were not called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.query_dn.assert_not_called()
        self.assertEqual(result, ({'status': 403, 'message': 'Forbiden', 'stack': ''}, 403))

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetChassisInternalServerError(self, mock_ucs):
        """Invoke a 500 http error"""
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = True
        mock_ucs.return_value.logout.return_value = True
        mock_ucs.return_value.query_children.side_effect = ["", "", ""]
        # call getCaltalog
        result = controler.getChassis(HOST, USER, PASS)
        # verify UCS Mocks were called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        # verify return data
        self.assertEqual(result, ({'status': 500, 'message': "Couldn't fetch EquipmentChassis", 'stack': ''}, 500))
