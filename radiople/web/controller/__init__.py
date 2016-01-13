# -*- coding: utf-8 -*-

from flask import Blueprint

bp_index = Blueprint('bp_index', __name__)
bp_auth = Blueprint('bp_auth', __name__, url_prefix='/auth')

from radiople.web.controller import auth
from radiople.web.controller import index


def start_routing(app):
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_index)
    print(app.url_map)
