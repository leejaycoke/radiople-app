# -*- coding: utf-8 -*-

import os
import random
import uuid

from datetime import datetime

from flask import Flask
from flask import abort
from flask import jsonify
from flask import request
from flask import Response
from flask.ext.cors import cross_origin

from mutagen.mp3 import MP3

from radiople.config import config
from radiople.libs.response import json_response
from radiople.libs.permission import AudioAuthorization
from radiople.libs.permission import ApiAuthorization
from radiople.libs.permission import Position

from radiople.model.role import Role

from radiople.service.audio import service as audio_service
from radiople.service.storage import Service as StorageService

from radiople.audio.response.audio import AudioResponse

from radiople.exceptions import BadRequest
from radiople.exceptions import RadiopleException


app = Flask(__name__)

app.debug = config.common.flask.debug

app.config['MAX_CONTENT_LENGTH'] = config.audio.upload.max_size


@app.errorhandler(RadiopleException)
def http_error_response(error):
    status_code = int(error.data['code'].split('.')[0])
    return jsonify(error.data), status_code


SERVERS = config.audio.upload.servers.split(',')

ALLOWED_MIMES = set(['audio/mpeg', 'audio/mp3'])


@app.route('/generate-temp-url', methods=['GET'])
@cross_origin()
@AudioAuthorization(Role.DJ, Role.ADMIN, position=Position.URL)
@json_response()
def get_temp_url():
    filename = uuid.uuid4().hex + '.mp3'
    storage_service = StorageService(config.common.storage.audio_container)
    temp_url = storage_service.generate_temp_url(filename, method='PUT')

    return {
        'filename': filename,
        'temp_url': temp_url
    }


@app.route('/', methods=['PUT'])
@cross_origin()
@ApiAuthorization(Role.DJ, Role.ADMIN, position=Position.URL)
@json_response(AudioResponse)
def upload_put():
    audio_file = request.files.get('file')
    if not audio_file:
        raise BadRequest

    filename = uuid.uuid4().hex
    path = random.choice(SERVERS) + datetime.now().strftime('%d/%m/%Y/')

    if not os.path.isdir(path):
        os.makedirs(path)

    dest = path + filename

    audio_file.save(dest)

    try:
        audio = MP3(dest)

        if audio.info.protected:
            raise BadRequest
    except:
        os.remove(dest)
        raise BadRequest('잘못된 mp3파일입니다.')

    if not ALLOWED_MIMES.intersection(audio.mime):
        os.remove(dest)
        raise BadRequest('잘못된 형식의 mp3파일입니다.')

    audio = audio_service.insert(
        filename=filename,
        user_id=request.auth.user_id,
        upload_filename=audio_file.filename,
        mimes=audio.mime,
        path=path,
        size=os.path.getsize(dest),
        length=audio.info.length,
        sample_rate=audio.info.sample_rate,
        bitrate=audio.info.bitrate,
    )

    return audio


@app.route('/<string:filename>', methods=['GET'])
@ApiAuthorization(Role.ALL, position=Position.URL)
def audio_get(filename):
    audio = audio_service.get_by_filename(filename)
    if not audio:
        abort(404)

    return redirect_audio(audio)


def redirect_audio(audio):
    response = Response()
    response.status_code = 206
    response.headers["X-Accel-Redirect"] = audio.full_filepath
    response.headers["Content-Type"] = 'audio/mpeg'
    response.headers['X-Accel-Buffering'] = 'no'
    return response
