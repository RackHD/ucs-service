# Copyright 2017, Dell EMC, Inc.

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

config = util.load_config(defaults)
context = util.setup_ssl_context(config)
app = connexion.App(__name__, specification_dir='./swagger/')
app.add_api('swagger.yaml', arguments={'title': 'UCS Service'})

# Global handlers are used to save UCSM login/logout actions
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
    print "Global handlers are cleared"

if __name__ == '__main__':
    app.run(
        host=config['address'],
        port=config['port'],
        debug=config['debug'],
        ssl_context=context
    )
