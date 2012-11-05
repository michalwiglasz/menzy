# -*- coding: utf-8 -*-

from flask import Flask
from menzy.api import api
import argparse


app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', metavar='N', type=int)
    parser.add_argument('--production', action='store_true')
    args = parser.parse_args()

    debug = not args.production
    app.run(host='0.0.0.0', port=args.port, debug=debug)
