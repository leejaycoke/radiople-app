# -*- coding: utf-8 -*-

from radiople.api.controller import api_v1

from radiople.libs.permission import ApiAuthorization
from radiople.libs.response import view_response

from radiople.model.role import Role

from radiople.service.agreement import api_service as agreement_service


@api_v1.route('/notice/opensource', methods=['GET'])
@ApiAuthorization(Role.ALL)
@view_response('opensource/index.html')
def notice_opensource_get():
    return dict()
