# -*- coding: utf-8 -*-

from flask import Blueprint

bp_index = Blueprint('bp_index', __name__)
bp_auth = Blueprint('bp_auth', __name__, url_prefix='/auth')
bp_broadcast = Blueprint('bp_broadcast', __name__, url_prefix='/broadcast')
bp_episode = Blueprint('bp_episode', __name__, url_prefix='/episode')
bp_dashboard = Blueprint('bp_dashboard', __name__, url_prefix='/dashboard')
bp_category = Blueprint('bp_category', __name__, url_prefix='/category')
bp_audio = Blueprint('bp_audio', __name__, url_prefix='/audio')

from radiople.console.controller import index
from radiople.console.controller import auth
from radiople.console.controller import broadcast
from radiople.console.controller import episode
from radiople.console.controller import category
from radiople.console.controller import dashboard
from radiople.console.controller import audio


def start_routing(app):
    app.register_blueprint(bp_index)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_broadcast)
    app.register_blueprint(bp_episode)
    app.register_blueprint(bp_category)
    app.register_blueprint(bp_dashboard)
    app.register_blueprint(bp_audio)
    print(app.url_map)
