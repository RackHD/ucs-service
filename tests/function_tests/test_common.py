'''
Copyright 2017, Dell EMC, Inc.

UCS test common methods and functions

'''

import os
import sys
import json
import requests

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecurePlatformWarning
)
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.SNIMissingWarning
)
sys.path.append("/".join((os.path.split(os.path.realpath(__file__))[0]).split('/')[:-2]))

from util import util  # noqa: E402

UCSM_CONFIG = json.loads(os.getenv('UCSCONFIG'))

UCSM_IP = UCSM_CONFIG.get("ucs-host")
UCSM_USER = UCSM_CONFIG.get("ucs-user")
UCSM_PASS = UCSM_CONFIG.get("ucs-pass")
UCS_SERVICE_CONFIG = util.load_config()

if UCS_SERVICE_CONFIG["httpsEnabled"]:
    UCS_SERVICE_URI = "https://{}:{}".format(
        UCS_SERVICE_CONFIG["address"],
        UCS_SERVICE_CONFIG["port"]
    )
else:
    UCS_SERVICE_URI = "http://{}:{}".format(
        UCS_SERVICE_CONFIG["address"],
        UCS_SERVICE_CONFIG["port"]
    )

def request(method, api, query=None, payload=None, headers=None):
    """
    Local HTTP/HTTPS request method
    """
    if not headers:
        headers = {
            "ucs-user": UCSM_USER,
            "ucs-password": UCSM_PASS,
            "ucs-host": UCSM_IP
        }
    url = UCS_SERVICE_URI + api
    response = getattr(requests, method)(
        url=url,
        verify=False,
        headers=headers,
        params=query,
        data=payload
    )
    return {"status": response.status_code, "json": response.json()}
