# Copyright 2017, Dell EMC, Inc.

import unittest
import controllers.default_controller as controler
import mock

EXPECTED_COOKIE = 'chocolate chip'
HOST = 'hostname'
USER = 'somebody'
PASS = 'secret'

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


