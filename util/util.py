#!/usr/bin/env python

def cleanup_ucs_handler(handler_obj):
    """
    Clean up UCS handler object
    """
    if not (handler_obj and isinstance(handler_obj, dict)):
        return None
    for handler in handler_obj.values():
        handler["ucs-handle"].logout()

def serialize_ucs_http_headers(headers):
    """
    Serialize ucs http headers
    """
    return {
        "ucs-host": headers.get("ucs-host"),
        "ucs-user": headers.get("ucs-user"),
        "ucs-password": headers.get("ucs-password")
    }
