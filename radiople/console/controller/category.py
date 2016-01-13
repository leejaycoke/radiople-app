# -*- coding: utf-8 -*-

from radiople.console.controller import bp_category

from radiople.libs.permission import ConsolePermission
from radiople.libs.response import json_response

from radiople.service.category import console_service as category_service

from radiople.console.response.category import CategoriesResponse


@bp_category.route('', methods=['GET'])
@ConsolePermission()
@json_response()
def get():
    categories = category_service.get_all()
    return CategoriesResponse({'categories': categories})
