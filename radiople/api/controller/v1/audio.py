# -*- coding: utf-8 -*-

from flask import send_file

from radiople.api.controller import api_v1

from radiople.libs.response import json_response

from radiople.service.audio import api_service as audio_service


from radiople.exceptions import NotFound


@api_v1.route('/audio/<string:filename>', methods=['GET'])
@json_response()
def audio_get(filename):
    audio = audio_service.get_by_filename(filename)
    if not audio:
        raise NotFound("해당 에피소드의 음원을 찾을 수 없습니다.")

    return send_file(audio.full_filepath, mimetype=audio.mime)
