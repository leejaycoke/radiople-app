# -*- coding: utf-8 -*-

from flask import request

from radiople.api.controller import api_v1

from radiople.libs.permission import ApiAuthorization
from radiople.libs.response import view_response

from radiople.model.role import Role

from radiople.service.opensource import api_service as opensource_service

from radiople.exceptions import BadRequest


@api_v1.route('/opensource/android', methods=['GET'], defaults={'os': 'android'})
@api_v1.route('/opensource/ios', methods=['GET'], defaults={'os': 'ios'})
@ApiAuthorization(Role.ALL)
@view_response('opensource/index.html')
def opensource_get(os):
    app_version = request.args.get('app_version', '0.1.0')
    opensource = opensource_service.get_by_os_app_version(os, app_version)
    return {'opensource': opensource}
