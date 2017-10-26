# Copyright 2017, Dell EMC, Inc.

import connexion
import json

defaults = {
    "address": "0.0.0.0",
    "port": 7080,
    "httpsEnabled": False,
    "certFile": None,
    "keyFile": None,
    "debug": False,
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
application = app.app

if __name__ == '__main__':
    app.run(
        host=config['address'],
        port=config['port'],
        debug=config['debug'],
        ssl_context=context)
