# -*- coding: utf-8 -*-

from flask import Flask
from flask import jsonify

from radiople.db import Session
from radiople.config import config

from radiople.helper import append_size

from radiople.exceptions import RadiopleException


app = Flask(__name__)

app.debug = config.common.flask.debug

app.jinja_env.filters['append_size'] = append_size


@app.errorhandler(RadiopleException)
def http_error_response(error):
    status_code = int(error.data['code'].split('.')[0])
    return jsonify(error.data), status_code


@app.teardown_request
def session_clear(exception=None):
    Session.remove()
    if exception and Session.is_active:
        Session.rollback()

from radiople.web.controller import start_routing

start_routing(app)
