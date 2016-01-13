# -*- coding: utf-8 -*-

from radiople.libs.response import view_response

from radiople.libs.permission import ConsolePermission

from radiople.console.controller import bp_dashboard


@bp_dashboard.route('/index.html', methods=['GET'])
@ConsolePermission()
@view_response('dashboard/index.html')
def index_html():
    pass
