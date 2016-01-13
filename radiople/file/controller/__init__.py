# -*- coding: utf-8 -*-

from radiople.file import app
from flask import Blueprint

bp_audio = Blueprint('bp_audio', __name__, url_prefix='/audio')

from radiople.file.controller import audio

app.register_blueprint(bp_audio)
