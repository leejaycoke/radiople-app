# -*- coding: utf-8 -*-

import os
import uuid

from flask import Flask
from flask import abort
from flask import redirect
from flask import jsonify
from flask import request
from flask.ext.cors import cross_origin

from mutagen.mp3 import MP3

from radiople.db import Session

from radiople.config import config
from radiople.libs.response import json_response
from radiople.libs.permission import AudioAuthorization
from radiople.libs.permission import Position
from radiople.libs.conoha import ConohaStorage

from radiople.model.role import Role

from radiople.service.audio import service as audio_service
from radiople.service.storage import service as storage_service
from radiople.service.storage_log import service as storage_log_service
from radiople.service.storage import Service as StorageService

from radiople.audio.response.audio import AudioResponse

from radiople.exceptions import BadRequest
from radiople.exceptions import ServerError
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

ALLOWED_MIMES = set(['audio/mpeg', 'audio/mp3'])


@app.route('/', methods=['PUT'])
@cross_origin()
@AudioAuthorization(Role.DJ, Role.ADMIN, position=Position.URL)
@json_response(AudioResponse)
def upload():
    audio_file = request.files.get('file')
    if not audio_file:
        raise BadRequest("파일이 업로드되지 않았습니다.")

    filename = uuid.uuid4().hex + '.mp3'

    dest = config.audio.upload.temp_path + filename

    try:
        audio_file.save(dest)
    except:
        raise ServerError("죄송합니다. 서버 하드디스크 용량이 부족합니다.")

    try:
        audio = MP3(dest)

        if audio.info.protected:
            raise BadRequest("파일 정보를 확인할 수 없습니다.")
    except:
        os.remove(dest)
        raise BadRequest('잘못된 mp3파일입니다.')

    if not ALLOWED_MIMES.intersection(audio.mime):
        os.remove(dest)
        raise BadRequest('잘못된 형식의 mp3파일입니다.')

    storage_service = StorageService()

    data = storage_service.put_audio(dest)
    if not data:
        os.remove(dest)
        raise ServerError("죄송합니다. 도저히 알 수 없는 문제가 발생했습니다.")

    audio = audio_service.insert(
        filename=data['filename'],
        user_id=request.auth.user_id,
        upload_filename=audio_file.filename,
        mimes=audio.mime,
        size=os.path.getsize(dest),
        length=audio.info.length,
        sample_rate=audio.info.sample_rate,
        bitrate=audio.info.bitrate,
        url=data['url']
    )

    os.remove(dest)

    return audio


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
