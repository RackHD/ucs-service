# Copyright 2017, Dell EMC, Inc.

import unittest
import mock
import tasks

MOCK_TASK_ID = "task_id"
MOCK_POLLER_DATA = {"data": "mock_poller_data"}
MOCK_ARGS = ("arg1", "arg2")
MOCK_KWARGS = {"arg3": "arg3"}

class test_default_tasks(unittest.TestCase):

    def setUp(self):
        print "tasks tests running setup"

    def tearDown(self):
        print "tasks tests running tear down"

    class mockRequestResponse:
        def __init__(self):
            self.status_code = 201
            self.content = "mock_request_response_data"

    @mock.patch('tasks.requests.request')
    @mock.patch('tasks.Celery')
    @mock.patch('tasks.Ucs.getPollers')
    def testSentHttpRequest(self, mock_ucs_get_pollers, mock_celery, mock_request):
        """Test sendHttpRequest task"""
        mock_request.return_value = self.mockRequestResponse()
        tasks.sendHttpRequest(MOCK_TASK_ID, MOCK_POLLER_DATA)
        mock_request.assert_called_once_with(
            "POST",
            tasks.callbackUrl,
            data=MOCK_POLLER_DATA,
            headers={'content-type': 'application/json'},
            params={"taskId": MOCK_TASK_ID}
        )

    @mock.patch('tasks.sendHttpRequest')
    @mock.patch('tasks.Celery')
    @mock.patch('tasks.Ucs.getPollers')
    def testRunUcsJob(self, mock_ucs_get_pollers, mock_celery, mock_send_http_request):
        """Test runUcsJob task"""
        mock_ucs_get_pollers.return_value = MOCK_POLLER_DATA
        mock_send_http_request.delay.return_value = "test"
        tasks.runUcsJob("getPollers", MOCK_TASK_ID, *MOCK_ARGS, **MOCK_KWARGS)
        kwargs_with_handler = {"handlers":{}}
        kwargs_with_handler.update(MOCK_KWARGS)
        mock_ucs_get_pollers.assert_called_once_with(*MOCK_ARGS, **kwargs_with_handler)
        mock_send_http_request.delay.assert_called_once_with(
            MOCK_TASK_ID,
            MOCK_POLLER_DATA
        )



