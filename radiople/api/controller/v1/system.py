# -*- coding: utf-8 -*-

from radiople.api.controller import api_v1

from radiople.libs.response import json_response

from radiople.api.common import extract_user_agent
from radiople.api.response.v1.system import SystemCheckResponse

from radiople.service.client_version import api_service as client_version_service
from radiople.service.static_image import api_service as static_image_service

from radiople.exceptions import BadRequest


@api_v1.route('/system/check', methods=['GET'])
@json_response(SystemCheckResponse)
def system_check_get():
    user_agent = extract_user_agent()

    if not user_agent:
        raise BadRequest

    os = user_agent.get('os')
    app_version = user_agent.get('app_version')

    client_version = client_version_service.get(os, app_version)

    static_images = static_image_service.get_all()

    return {
        'client_version': client_version,
        'static_images': static_images
    }
