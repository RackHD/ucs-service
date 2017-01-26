# Copyright 2017, Dell EMC, Inc.

import connexion

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'UCS Service'})
    app.run(host='0.0.0.0', port=7080)
