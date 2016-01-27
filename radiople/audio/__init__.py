# -*- coding: utf-8 -*-

from flask import Flask
from flask import abort
from flask import jsonify
from flask import request

from radiople.db import Session

from radiople.config import config
from radiople.libs.response import json_response
from radiople.libs.permission import AudioAuthorization
from radiople.libs.permission import Position
from radiople.libs.conoha import ConohaStorage

from radiople.model.role import Role

from radiople.service.storage import service as storage_service
from radiople.service.storage_log import service as storage_log_service

from radiople.exceptions import RadiopleException


app = Flask(__name__)

app.debug = config.common.flask.debug

app.config['MAX_CONTENT_LENGTH'] = config.audio.upload.max_size


@app.errorhandler(RadiopleException)
def http_error_response(error):
    status_code = int(error.data['code'].split('.')[0])
    return jsonify(error.data), status_code


@app.teardown_request
def session_clear(exception=None):
    Session.remove()
    if exception and Session.is_active:
        Session.rollback()

OBJECT_TEMP_EXPIRES = 36000


@app.route('/<string:d>/<string:m>/<string:y>/<string:filename>', methods=['GET'])
@json_response()
@AudioAuthorization(Role.ALL, position=Position.URL)
def get_object(d, m, y, filename):
    storage_object = storage_service.get_by_filename(filename)
    if not storage_object:
        abort(404)

    full_filename = '/%s/%s/%s/%s' % (d, m, y, filename)

    conoha_storage = ConohaStorage()
    temp_url = conoha_storage.generate_temp_url(
        full_filename, seconds=OBJECT_TEMP_EXPIRES)

    user_id = 0 if request.auth.is_guest() else request.auth.user_id

    storage_log_service.insert(
        user_id=user_id,
        service=request.auth.service,
        storage_id=storage_object.id
    )

    return {
        'urls': [
            {'url': temp_url, 'type': 'audio'}
        ]
    }
