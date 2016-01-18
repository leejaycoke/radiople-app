# -*- coding: utf-8 -*-

from radiople.libs.response import view_response

from radiople.libs.permission import ConsoleAuthorization

from radiople.console.controller import bp_dashboard


@bp_dashboard.route('/index.html', methods=['GET'])
@ConsoleAuthorization()
@view_response('dashboard/index.html')
def index_html():
    pass
