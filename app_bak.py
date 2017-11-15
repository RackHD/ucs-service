# Copyright 2017, Dell EMC, Inc.

import atexit
import connexion
from flask import current_app
from util import util

config = util.load_config()
context = util.setup_ssl_context(config)
app = connexion.App(__name__, specification_dir='./swagger/')
app.add_api('swagger.yaml', arguments={'title': 'UCS Service'})

# Global handlers in current_app.config are used to minimize UCSM login/logout operations
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
    print "Global handlers for connexion/flask app are cleared"


if __name__ == '__main__':
    app.run(
        host=config['address'],
        port=config['port'],
        debug=config['debug'],
        ssl_context=context
    )
