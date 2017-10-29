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
MOCK_TASK_ID = "12345"
MOCK_ID = "abc"


class test_default_async_controller(unittest.TestCase):

    def setUp(self):
        print "running async controller tests setup"

    def tearDown(self):
        print "running async controller tests teardown"

    @mock.patch('controllers.ucs_async_controller.request')
    @mock.patch('controllers.ucs_async_controller.tasks.runUcsJob')
    def testGetPollersSuccess(self, mock_tasks, mock_request):
        """Get pollers asynchronously"""
        mock_tasks.delay.return_value = True
        mock_request.headers = MOCK_HEADER
        result = controler.getPollersAsync(MOCK_ID, MOCK_CLASS_IDS, MOCK_TASK_ID)
        mock_tasks.delay.assert_called_once_with(
            "getPollers",
            MOCK_TASK_ID,
            MOCK_HEADER,
            MOCK_ID,
            MOCK_CLASS_IDS
        )
        self.assertEqual(result[0], "Accepted")
