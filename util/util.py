# Copyright 2017, Dell EMC, Inc.

import json

CONFIG_FILE = 'config.json'

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


def load_config(defaults):
    """
    Load configuration from config file
    """
    config = {}
    try:
        with open(CONFIG_FILE) as config_data:
            config = json.load(config_data)
    except:
        print "Error loading config.json, using defaults!"
        config = defaults
    return config


def setup_ssl_context(config):
    """
    Setup ssl context for connexion/flask app
    """
    if 'httpsEnabled' not in config or not config['httpsEnabled']:
        context = None
    elif 'certFile' not in config or config['certFile'] is None or \
        'keyFile' not in config or config['keyFile'] is None:
        context = 'adhoc'
    else:
        context = (config['certFile'], config['keyFile'])
    return context
