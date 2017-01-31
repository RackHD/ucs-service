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
        self.assertNotIn('_privData', result, 'result contains private member "_privData"')

    @mock.patch('controllers.default_controller.UcsHandle')
    def testGetCatalogFailure(self, mock_ucs):
        # setup UCS mocks
        mock_ucs.return_value.login.return_value = False
        # call getCaltalog
        result = controler.getCatalog(HOST, USER, PASS, identifier=MOCK_ID)
        # verify UCS Mocks were not called
        mock_ucs.assert_called_with(HOST, USER, PASS, secure=False)
        mock_ucs.return_value.login.assert_called_once()
        mock_ucs.return_value.query_dn.assert_not_called()
        mock_ucs.return_value.logout.assert_not_called()
        self.assertIsNone(result)
