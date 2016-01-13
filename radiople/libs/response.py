# -*- coding: utf-8 -*-

from functools import wraps

from flask import request
from flask import jsonify
from flask import render_template

from marshmallow import Schema
from marshmallow.schema import SchemaMeta


def json_response(serializer=dict):
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            data = func(*args, **kwargs)

            if not data:
                return jsonify({})

            if isinstance(serializer, SchemaMeta):
                result = serializer().dump(data)
                return jsonify(result.data)

            if isinstance(serializer, Schema):
                result = serializer.dump(data)
                return jsonify(result.data)

            if isinstance(serializer, dict):
                return jsonify(data)

            return jsonify({})

        return func_wrapper
    return decorator


def view_response(layout, bp=None):
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            data = func(*args, **kwargs) or dict()

            if isinstance(data, SchemaMeta):
                return jsonify(data.data)

            paths = [p.strip()
                     for p in request.path.split('/') if p.strip() != '']

            constants = {
                'controller': paths[0] if paths else 'index'
            }

            if isinstance(data, dict):
                return render_template(layout, constants=constants, **data)

            return data

        return func_wrapper
    return decorator


def angular_response(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        html, json = func(*args, **kwargs)

        if not request.is_xhr:
            return html()
        return json()

    return decorator
