# -*- coding: utf-8 -*-

from os import path

from flask import Flask
from flask import jsonify
from flask.ext.cache import Cache

from radiople.db import Session
from radiople.config import config

from radiople.exceptions import RadiopleException
from radiople.exceptions import ServiceUnavailable


_SCRIPT_PATH = path.join(path.dirname(path.realpath(__file__)))
_STATIC_PATH = path.realpath(path.join(_SCRIPT_PATH, '../static'))

app = Flask(__name__, static_folder=_STATIC_PATH)


app.debug = config.common.flask.debug

if app.debug:
    import sqltap.wsgi

app.wsgi_app = sqltap.wsgi.SQLTapMiddleware(app.wsgi_app)

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'cache',
    'CACHE_REDIS_URL': config.common.cache.uri
})


@app.before_request
def before_request():
    maintenance = config.common.maintenance
    if maintenance.is_active:
        raise ServiceUnavailable(maintenance.message)


@app.errorhandler(RadiopleException)
def http_error_response(error):
    status_code = int(error.data['code'].split('.')[0])
    return jsonify(error.data), status_code


@app.teardown_request
def session_clear(exception=None):
    Session.remove()
    if exception and Session.is_active:
        Session.rollback()

from radiople.api import controller

controller.start_routing(app)
