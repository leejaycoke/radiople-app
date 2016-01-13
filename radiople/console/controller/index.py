# -*- coding: utf-8 -*-

from flask import redirect
from flask import url_for

from radiople.console.controller import bp_index


@bp_index.route('/', methods=['GET'])
def index_get():
    return redirect(url_for('bp_user.signin_html'))
