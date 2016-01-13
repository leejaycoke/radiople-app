# -*- coding: utf-8 -*-

from flask import Blueprint

api_auth = Blueprint('api_auth', __name__, url_prefix='/auth')
api_v1 = Blueprint('api_v1', __name__, url_prefix='/v1')

from radiople.api.controller import auth
from radiople.api.controller.v1 import *


def start_routing(app):
    app.register_blueprint(api_auth)
    app.register_blueprint(api_v1)
    print(app.url_map)
