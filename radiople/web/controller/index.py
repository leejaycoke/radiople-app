# -*- coding: utf-8 -*-

from flask import request

from radiople.web.controller import bp_index

from radiople.libs.response import view_response


@bp_index.route('/', methods=['GET'])
@view_response('index/index.html')
def index_get():
    print(dir(request))
    print(request.view_args)
    pass
