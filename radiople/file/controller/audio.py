# -*- coding: utf-8 -*-

import os

import random

import uuid

from datetime import datetime

from mutagen.mp3 import MP3

from flask import request
from flask.ext.cors import cross_origin

from radiople.file.controller import bp_audio
from radiople.file.response.audio import AudioResponse

from radiople.config import config
from radiople.libs.response import json_response

from radiople.exceptions import BadRequest

from radiople.service.audio import service as audio_service


SERVERS = config.audio.upload.servers.split(',')

ALLOWED_MIMES = set(['audio/mpeg', 'audio/mp3'])


@bp_audio.route('', methods=['PUT'])
@cross_origin()
@json_response()
def upload():
    audio_file = request.files.get('file')
    if not audio_file:
        raise BadRequest

    filename = uuid.uuid4().hex
    path = random.choice(SERVERS) + datetime.now().strftime('%d/%m/%y/')

    if not os.path.isdir(path):
        os.makedirs(path)

    dest = path + filename

    audio_file.save(dest)

    try:
        audio = MP3(dest)
    except:
        raise BadRequest('잘못된 mp3파일입니다.')

    if not ALLOWED_MIMES.intersection(audio.mime):
        raise BadRequest('잘못된 형식의 mp3파일입니다.')

    audio = audio_service.insert(
        filename=filename,
        upload_filename=audio_file.filename,
        mimes=audio.mime,
        path=path,
        size=os.path.getsize(dest),
        length=audio.info.length,
        sample_rate=audio.info.sample_rate,
        bitrate=audio.info.bitrate,
    )

    return AudioResponse(audio)


@bp_audio.route('', methods=['DELETE'])
def delete():
    pass


@bp_audio.route('', methods=['GET'])
def get():
    pass
