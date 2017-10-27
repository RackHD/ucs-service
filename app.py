# Copyright 2017, Dell EMC, Inc.

import json
import atexit
import connexion
from flask import current_app
from util import util

defaults = {
    "address": "0.0.0.0",
    "port": 7080,
    "httpsEnabled": False,
    "certFile": None,
    "keyFile": None,
    "debug": False
}

# load config info
try:
    with open('config.json') as config_data:
        config = json.load(config_data)
except:
    print("Error loading config.json, using defaults!")
    config = defaults

# set up ssl_context
if 'httpsEnabled' not in config or not config['httpsEnabled']:
    context = None
elif 'certFile' not in config or config['certFile'] is None or \
        'keyFile' not in config or config['keyFile'] is None:
    context = 'adhoc'
else:
    context = (config['certFile'], config['keyFile'])

app = connexion.App(__name__, specification_dir='./swagger/')
app.add_api('swagger.yaml', arguments={'title': 'UCS Service'})

with app.app.app_context():
    current_app.config['handlers'] = {}

@atexit.register
def cleanup():
    """
    App clean up
    """
    with app.app.app_context():
        handlers = current_app.config.get("handlers")
        util.cleanup_ucs_handler(handlers)

if __name__ == '__main__':
    app.run(
        host=config['address'],
        port=config['port'],
        debug=config['debug'],
        ssl_context=context
    )
