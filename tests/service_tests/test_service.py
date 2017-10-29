# Copyright 2017, Dell EMC, Inc.

import unittest
import mock
import service.ucs as service

HOST = 'hostname'
USER = 'somebody'
PASS = 'secret'
MOCK_HEADER = {
    'ucs-host': HOST,
    'ucs-password': PASS,
    'ucs-user': USER
}


class test_default_service(unittest.TestCase):

    def setUp(self):
        print "service tests running setup"

    def tearDown(self):
        print "service tests running tear down"

    class mockUcsHandle:
        result = True
        def __init__(self):
            pass

        def logout(self):
            return False

        def login(self):
            return self.result

    @mock.patch('service.ucs.UcsHandle')
    @mock.patch('service.ucs.time')
    def test_getHandlerSuccess1(self, mock_time, mock_ucs_handle_cls):
        """Get handler successfully with existing handler"""
        mock_time.time.return_value = 1
        mock_ucs_handle_obj = {
            'timestamp': 0,
            'ucs-handle': self.mockUcsHandle(),
            'ucs-user': USER,
            'ucs-password': PASS,
            'ucs-host': HOST
        }
        mock_ucs_handlers = {}
        mock_ucs_handlers[HOST] = mock_ucs_handle_obj
        result = service.Ucs._getHandler(MOCK_HEADER, mock_ucs_handlers)
        self.assertEqual(mock_ucs_handle_obj["ucs-handle"], result)
        mock_ucs_handle_cls.assert_not_called()

    @mock.patch('service.ucs.UcsHandle')
    @mock.patch('service.ucs.time')
    def test_getHandlerSuccess2(self, mock_time, mock_ucs_handle_cls):
        """Get handler successfully with new handler"""
        mock_ucs_handle_cls.return_value.login.return_value = True
        mock_time.time.return_value = 61
        mock_ucs_handle_obj = {
            'timestamp': 0,
            'ucs-handle': self.mockUcsHandle(),
            'ucs-user': USER,
            'ucs-password': PASS,
            'ucs-host': HOST
        }
        mock_ucs_handlers = {}
        mock_ucs_handlers[HOST] = mock_ucs_handle_obj
        result = service.Ucs._getHandler(MOCK_HEADER, mock_ucs_handlers)
        self.assertEqual(mock_ucs_handle_cls.return_value, result)
        mock_ucs_handle_cls.assert_called_once_with(HOST, USER, PASS, secure=False)
        mock_ucs_handle_cls.return_value.login.assert_called_once()

    @mock.patch('service.ucs.UcsHandle')
    @mock.patch('service.ucs.time')
    def test_getHandlerFailed(self, mock_time, mock_ucs_handle_cls):
        """Get handler failed"""
        mock_ucs_handle_cls.return_value.login.return_value = False
        mock_ucs_handle_cls.return_value.login_out.return_value = True
        mock_time.time.return_value = 61
        mock_ucs_handle_obj = {
            'timestamp': 0,
            'ucs-handle': self.mockUcsHandle(),
            'ucs-user': USER,
            'ucs-password': PASS,
            'ucs-host': HOST
        }
        mock_ucs_handlers = {}
        mock_ucs_handlers[HOST] = mock_ucs_handle_obj
        result = service.Ucs._getHandler(MOCK_HEADER, mock_ucs_handlers)
        self.assertEqual(result, None)
        mock_ucs_handle_cls.assert_called_once_with(HOST, USER, PASS, secure=False)
        mock_ucs_handle_cls.return_value.login.assert_called_once()
        mock_ucs_handle_cls.return_value.logout.assert_called_once()
