# -*- coding: utf-8 -*-


from flask import Flask
from flask import jsonify

from radiople.config import config

from radiople.exceptions import RadiopleException


app = Flask(__name__)

app.debug = config.common.flask.debug


@app.errorhandler(RadiopleException)
def http_error_response(error):
    status_code = int(error.data['code'].split('.')[0])
    return jsonify(error.data), status_code


from radiople.media import controller
