# -*- coding: utf-8 -*-

from radiople.api.controller import api_v1

from radiople.libs.permission import ApiPermission
from radiople.libs.response import view_response

from radiople.service.agreement import api_service as agreement_service


@api_v1.route('/agreement/<string:type>', methods=['GET'])
@ApiPermission(guest_ok=True)
@view_response('agreement.html')
def agreement_get(type):
    agreement = agreement_service.get_by_type(type)
    return dict(agreement=agreement)
