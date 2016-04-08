# -*- coding: utf-8 -*-

from flask import Blueprint

bp_index = Blueprint('bp_index', __name__)
bp_auth = Blueprint('bp_auth', __name__, url_prefix='/auth')
bp_agreement = Blueprint('bp_agreement', __name__, url_prefix='/agreement')

from radiople.web.controller import auth
from radiople.web.controller import index
from radiople.web.controller import agreement


def start_routing(app):
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_index)
    app.register_blueprint(bp_agreement)
    print(app.url_map)
