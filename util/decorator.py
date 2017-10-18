# Copyright 2017, Dell EMC, Inc.
import traceback
from ucsmsdk.ucsexception import UcsException


def response_wrapper(function):
    def wrapper(*args, **kwargs):
        resp = function(*args, **kwargs)
        if (len(resp) == 3):
            http_res = {
                "message": resp[0],
                "status": resp[2],
                "stack": resp[1]
            }
            return http_res, resp[2]
        else:
            return resp

    return wrapper


def status_handler(default_status=200):
    def outter(function):
        def wrapper(*args, **kwargs):
            try:
                result = function(*args, **kwargs)
            except UcsException as e:
                return 'Internal Server Error', e.error_descr, 500
            except Exception as e:
                return 'Internal Server Error', traceback.format_exc(e), 500

            if result.get("data"):
                return result.get("data"), default_status
            elif result.get("error") == "Forbidden":
                return result.get("error"), "", 403
            elif result.get("error"):
                return result.get("error"), "", 500
            else:
                return "Unknown", "", 500

        return wrapper
    return outter
