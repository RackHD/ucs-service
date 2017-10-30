# Copyright 2017, Dell EMC, Inc.

import unittest
import mock
from util import util

MOCK_CONFIG = {
    "address": "0.0.0.0",
    "port": 7080,
    "httpsEnabled": True,
    "certFile": None,
    "keyFile": None
}

MOCK_DEFAULT = {
    "address": "0.0.0.0",
    "port": 8080,
    "httpsEnabled": False,
    "certFile": None,
    "keyFile": None
}

MOCK_SSL_CONFIG = {
    "httpsEnabled": True,
    "certFile": "cert_file",
    "keyFile": "key_file"
}


class test_default_tasks(unittest.TestCase):

    def setUp(self):
        print "util tests running setup"

    def tearDown(self):
        print "util tests running tear down"

    def sideEffect(self):
        raise KeyError

    class mockHandlerObj:
        def __init__(self, func):
            self.logout = func

    def testCleanupUcsHandlerSuccess(self):
        """Test clean up ucs handler successfully"""
        handler_obj = {}
        _mock = mock.Mock()
        for i in range(3):
            handler_obj[i] = {"ucs-handle": self.mockHandlerObj(_mock)}
        util.cleanup_ucs_handler(handler_obj)
        self.assertEqual(_mock.call_count, 3)

    def testCleanupUcsHandlerFailed(self):
        """Test clean up ucs handler failed"""
        result = util.cleanup_ucs_handler(None)
        self.assertEqual(result, None)

    @mock.patch('util.util.json')
    def testLoadConfigSuccess(self, mock_json):
        """Test load config file successfully"""
        mock_json.load.return_value = MOCK_CONFIG
        result = util.load_config(MOCK_DEFAULT)
        self.assertEqual(result, MOCK_CONFIG)

    @mock.patch('util.util.json')
    def testLoadConfigFailed(self, mock_json):
        """Test load config file failed"""
        mock_json.load.side_effect = self.sideEffect
        result = util.load_config(MOCK_DEFAULT)
        self.assertEqual(result, MOCK_DEFAULT)

    def testSetupSslContext(self):
        """Test setup ssl context"""
        result = util.setup_ssl_context(MOCK_CONFIG)
        self.assertEqual(result, 'adhoc')
        result = util.setup_ssl_context(MOCK_DEFAULT)
        self.assertEqual(result, None)
        result = util.setup_ssl_context(MOCK_SSL_CONFIG)
        self.assertEqual(result, (MOCK_SSL_CONFIG['certFile'], MOCK_SSL_CONFIG['keyFile']))
