# -*- coding: utf-8 -*-

import os
import uuid

from datetime import datetime

from PIL import Image
from PIL import ImageOps

from flask import Flask
from flask import jsonify
from flask import abort
from flask import request
from flask import send_file
from flask.ext.cors import cross_origin

from radiople.libs.response import json_response
from radiople.libs.permission import ApiPermission
from radiople.libs.permission import ConsoleAuthorization

from radiople.config import config

from radiople.exceptions import RadiopleException
from radiople.exceptions import BadRequest


app = Flask(__name__)

app.debug = config.common.flask.debug

app.config['MAX_CONTENT_LENGTH'] = config.image.upload.max_size


@app.errorhandler(RadiopleException)
def http_error_response(error):
    status_code = int(error.data['code'].split('.')[0])
    return jsonify(error.data), status_code


UPLOAD_PATH = config.image.upload.path
SERVER_URL = config.image.server.url


PERMISSION_MAP = {
    'api': ApiPermission,
    'console': ConsoleAuthorization
}


def get_permission_class():
    service = request.args.get('service', 'api')
    return PERMISSION_MAP.get(service)


@app.route('/', methods=['PUT'])
@cross_origin()
@json_response()
def upload_put():
    check_permission = get_permission_class()

    @check_permission(position='url')
    def put_upload():
        image_file = request.files.get('file')
        if not image_file:
            raise BadRequest

        raw_name = uuid.uuid4().hex
        raw_path = datetime.now().strftime('%d/%m/%Y/')
        path = UPLOAD_PATH + 'original/' + raw_path

        if not os.path.isdir(path):
            os.makedirs(path)

        try:
            image = Image.open(image_file)
            image_format = image.format

            filename = raw_name + '.' + image_format.lower()
            dest = path + filename

            image.save(dest, image.format, quality=85)
        except:
            raise BadRequest("이미지 파일만 업로드 가능합니다.")

        return {'url': SERVER_URL + '/' + raw_path + filename}

    return put_upload()


@app.route('/<string:d>/<string:m>/<string:y>/<string:filename>', methods=['GET'], defaults={'size': None})
@app.route('/<string:size>/<string:d>/<string:m>/<string:y>/<string:filename>', methods=['GET'])
def get(size, d, m, y, filename):
    base_path = UPLOAD_PATH + '%s/%s/%s/%s/' % (size or 'original', d, m, y)
    dest = base_path + filename

    if os.path.isfile(dest):
        return send_file(dest, mimetype='image/jpeg')

    if not size:
        abort(404)

    original = UPLOAD_PATH + 'original/%s/%s/%s/%s' % (d, m, y, filename)
    if not os.path.isfile(original):
        abort(404)

    if not os.path.isdir(base_path):
        os.makedirs(base_path)

    try:
        image = Image.open(original)
        image_format = image.format

        width, height = size.split('x')
        image = ImageOps.fit(image, (int(width), int(height)))
        image.save(dest, image_format, quality=85)
    except:
        abort(404)

    return send_file(dest, mimetype='image/jpeg')
