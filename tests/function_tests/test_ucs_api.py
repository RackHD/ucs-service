'''
Copyright 2017, Dell, Inc.

Author(s):

UCS test script that tests:
-All the ucs service APIs

'''

import unittest
from function_tests.test_common import request
from nosedep import depends
from nose.plugins.attrib import attr


@attr(all=True)
class ucs_api(unittest.TestCase):

    def test_ucs_log_in(self):
        """
        Test the /logIn ucs API
        :return:
        """
        api_data = request("get", "/login")
        self.assertEqual(api_data['status'], 200,
                         'Incorrect HTTP return code, expected 200, got:' + str(api_data['status']))
        self.assertNotEqual(api_data["json"], None,
                            "Expected a token to be returned on login and received None")
        self.assertNotEqual(type(api_data["json"]),
                            "unicode", "Unexpected Token was received on Login")

    def test_ucs_get_sys(self):
        """
        Test the /sys ucs API
        :return:
        """
        api_data = request("get", "/sys")
        self.assertEqual(api_data['status'], 200,
                         'Incorrect HTTP return code, expected 200, got:' + str(api_data['status']))
        self.assertIn("Fabric Interconnects", api_data["json"],
                      "Results did not contain 'Fabric Interconnects'")
        self.assertIn("Servers", api_data["json"], "Results did not contain 'Servers")
        self.assertIn("FEX", api_data["json"], "Results did not contain 'FEX")
        self.assertIn("Chassis", api_data["json"], "Results did not contain 'Chassis")

    def test_ucs_get_rackmount(self):
        """
        Test the /rackmount ucs API
        :return:
        """
        api_data = request("get", "/rackmount")
        self.assertEqual(api_data['status'], 200,
                         'Incorrect HTTP return code, expected 200, got:' + str(api_data['status']))
        self.assertGreater(len(api_data["json"]), 0, "Found zero Rackmounts")
        # TO DO more in depth testing for the returned content such as mac validation, etc...

    def test_ucs_get_chassis(self):
        """
        Test the /chassis ucs API
        :return:
        """
        api_data = request("get", "/chassis")
        self.assertEqual(api_data['status'], 200,
                         'Incorrect HTTP return code, expected 200, got:' + str(api_data['status']))
        self.assertGreater(len(api_data["json"]), 0, "Zero chassis elements found")
        # TO DO more in depth testing for the returned content such as mac validation, etc...

    @depends(after=[test_ucs_get_chassis])
    def test_ucs_get_serviceProfile(self):
        """
        Test the /serviceProfile ucs API
        :return:
        """
        api_data = request("get", "/serviceProfile")
        self.assertEqual(api_data['status'], 200,
                         'Incorrect HTTP return code, expected 200, got:' + str(api_data['status']))
        if len(api_data["json"]["ServiceProfile"]["members"]) == 0:
            raise unittest.SkipTest("No Service Profiles Defined")
        # TO DO more in depth testing for the returned content such as mac validation, etc...

    def test_api_20_ucs_get_catalog(self):
        """
        Test the /catalog ucs API
        :return:
        """
        api_data = request("get", "/sys")
        self.assertEqual(api_data['status'], 200,
                         'Incorrect HTTP return code, expected 200, got:' + str(api_data['status']))
        total_elements = 0
        for elementTypes in api_data["json"]:
            for element in api_data["json"][str(elementTypes)]:
                api_data_c = request("get", "/catalog",
                                     query={"identifier": element["relative_path"].strip("/")})
                self.assertEqual(api_data_c['status'], 200,
                                 'Incorrect HTTP return code, expected 200, got:' +
                                 str(api_data_c['status']))
                total_elements += 1
        self.assertGreater(total_elements, 0, "Zero catalog elements found")
        # TO DO: deeper check on the catalog data

    def check_all_server_power_state(self, state):
        """
        Test to see if all Associated servers are in the specified state
        :return: True or False
        """
        api_data = request("get", "/serviceProfile")
        self.assertEqual(api_data['status'], 200,
                         'Incorrect HTTP return code, expected 200, got:' + str(api_data['status']))
        total_elements = 0
        for server in api_data["json"]["ServiceProfile"]["members"]:
            if server["assoc_state"] == "associated":
                api_data_c = request("get", "/power",
                                     query={"identifier": str(server["path"])})
                self.assertEqual(api_data_c['status'], 200,
                                 'Incorrect HTTP return code, expected 200, got:' +
                                 str(api_data_c['status']))
                self.assertEqual(api_data_c["json"]["serverState"], state,
                                 'Server ' + str(server["path"]) + ' reported power state ' +
                                 str(api_data_c["json"]["serverState"]) + ' expected: ' + state)
            total_elements += 1
        self.assertGreater(total_elements, 0, "Found zero elements")

    def set_all_server_power_state(self, state):
        """
        Use the POST /power ucs API to set the state of all servers
        :return:
        """
        api_data = request("get", "/serviceProfile")
        self.assertEqual(api_data['status'], 200,
                         'Incorrect HTTP return code, expected 200, got:' + str(api_data['status']))
        total_elements = 0
        for server in api_data["json"]["ServiceProfile"]["members"]:
            if server["assoc_state"] == "associated":
                api_data_c = request("post", "/power",
                                     query={"identifier": str(server["path"]), "action": state})
                self.assertEqual(api_data_c['status'], 200,
                                 'Incorrect HTTP return code, expected 200, got:' +
                                 str(api_data_c['status']))
            total_elements += 1
        self.assertGreater(total_elements, 0, "Found zero elements")

    @depends(after=[test_ucs_get_serviceProfile])
    def test_api_20_ucs_power(self):
        """
        Test the GET and POST api for server power state
        :return:
        """
        # first power off all servers
        self.set_all_server_power_state("off")
        # verify power state is down
        self.check_all_server_power_state("down")
        # now power on the servers
        self.set_all_server_power_state("on")
        # verify power state is up
        self.check_all_server_power_state("up")


if __name__ == '__main__':
    unittest.main()
