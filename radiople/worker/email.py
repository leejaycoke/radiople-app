# -*- coding: utf-8 -*-

from radiople.worker import CeleryApp
from radiople.worker import RadiopleTask

from radiople.config import config

from radiople.service.user import service as user_service

from mandrill import Mandrill


worker = CeleryApp(RadiopleTask.EMAIL).app

mandrill = Mandrill(config.common.mandrill.api_key)


@worker.task
def send_email_validation(user_id, access_token):
    verify_url = "%s/%s?access_token=%s" % (
        config.web.server.url, "auth/email-validation", access_token)
    user = user_service.get(user_id)

    message = {
        'to': [{
            'email': user.email,
            'name': user.nickname
        }],
        'merge': True,
        'merge_language': 'handlebars',
        'global_merge_vars': [{
            'name': 'verify_url',
            'content': verify_url
        }]
    }

    mandrill.messages.send_template('email_validation', [], message)


@worker.task
def send_find_password(user_id, access_token):
    verify_url = "%s/%s?access_token=%s" % (
        config.web.server.url, "auth/reset-password", access_token)
    user = user_service.get(user_id)

    message = {
        'to': [{
            'email': user.email,
            'name': user.nickname
        }],
        'merge': True,
        'merge_language': 'handlebars',
        'global_merge_vars': [{
            'name': 'verify_url',
            'content': verify_url
        }]
    }

    mandrill.messages.send_template('find_password', [], message)
