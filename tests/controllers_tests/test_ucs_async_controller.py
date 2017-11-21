# Copyright 2017, Dell EMC, Inc.

import unittest
import mock
import controllers.ucs_async_controller as controler

HOST = 'hostname'
USER = 'somebody'
PASS = 'secret'
MOCK_HEADER = {
    'ucs-host': HOST,
    'ucs-password': PASS,
    'ucs-user': USER
}
MOCK_CLASS_IDS = ['processorEnvStats', 'memoryUnitEnvStats']
MOCK_CALLBACK_ID = "12345"
MOCK_ID = "abc"


class test_default_async_controller(unittest.TestCase):

    def setUp(self):
        print "running async controller tests setup"

    def tearDown(self):
        print "running async controller tests tear down"

    @mock.patch('controllers.ucs_async_controller.request')
    @mock.patch('controllers.ucs_async_controller.tasks.runUcsJob')
    def testGetPollersSuccess(self, mock_tasks, mock_request):
        """Get pollers asynchronously"""
        mock_tasks.delay.return_value = True
        mock_request.headers = MOCK_HEADER
        result = controler.getPollersAsync(MOCK_ID, MOCK_CLASS_IDS, MOCK_CALLBACK_ID)
        mock_tasks.delay.assert_called_once_with(
            "getPollers",
            MOCK_CALLBACK_ID,
            MOCK_HEADER,
            MOCK_ID,
            MOCK_CLASS_IDS
        )
        self.assertEqual(result[0], "Accepted")

    @mock.patch('controllers.ucs_async_controller.request')
    @mock.patch('controllers.ucs_async_controller.tasks.runUcsJob')
    def testGetCatalogAsyncSuccess(self, mock_tasks, mock_request):
        """Get catalog asynchronously"""
        mock_tasks.delay.return_value = True
        mock_request.headers = MOCK_HEADER
        result = controler.getCatalogAsync(MOCK_ID, MOCK_CALLBACK_ID)
        mock_tasks.delay.assert_called_once_with(
            "getCatalog",
            MOCK_CALLBACK_ID,
            MOCK_HEADER,
            MOCK_ID
        )
        self.assertEqual(result[0], "Accepted")
