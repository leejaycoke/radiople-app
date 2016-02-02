# -*- coding: utf-8 -*-

import uuid
import json
import requests

from dateutil import parser

from datetime import datetime
from datetime import timedelta

from swiftclient import utils
from swiftclient.client import Connection

from radiople.config import config


AUTH_URL = config.common.storage.auth_url
SIGNED_URL_KEY = config.common.storage.signed_url_key
AUTH_VERSION = config.common.storage.auth_version

USER_NAME = config.common.storage.user_name
KEY = config.common.storage.key
TENANT_ID = config.common.storage.tenant_id
TENANT_NAME = config.common.storage.tenant_name

STORAGE_FULL_URL = config.common.storage.full_url
STORAGE_URL = config.common.storage.url
STORAGE_PATH = config.common.storage.path

CONTAINER = config.common.storage.container


class ConohaStorage(object):

    connection = None
    token = None
    expires_at = None

    def refresh_token(self):
        data = json.dumps({
            'auth': {
                'passwordCredentials': {
                    'username': USER_NAME,
                    'password': KEY,
                },
                'tenantId': TENANT_ID
            }
        })

        response = self.request(
            'POST', AUTH_URL, data=data, is_auth_request=False)

        data = response.json()

        self.token = data['access']['token']['id']
        self.expires_at = data['access']['token']['expires']

    def head_object(self, filename):
        url = STORAGE_URL + filename
        response = self.request('HEAD', url)
        return response.headers

    def copy_object(self, src_obj, dst_obj):
        url = STORAGE_URL + src_obj
        response = self.request(
            'COPY', url, headers={'Destination': CONTAINER + '/' + dst_obj})
        return response.headers

    def rename_object(self, src_filename, dst_filename):
        self.copy_object(src_filename, dst_filename)
        self.delete_object(src_filename)

    def delete_object(self, obj):
        url = STORAGE_URL + obj
        response = self.request('DELETE', url)
        return response.headers

    def generate_temp_url(self):
        pass

    def expired(self):
        return self.token['expired_at'] <= datetime.now()

    def request(self, method, url, data={}, headers={}, is_auth_request=True):
        if is_auth_request and (not self.token or self.expired):
            self.refresh_token()

        headers.update({
            'Accept': 'application/json',
            'X-Auth-Token': self.token
        })

        params = {
            'method': method,
            'url': url,
            'headers': headers,
        }

        if method not in ['GET', 'HEAD'] and data:
            params['data'] = data

        response = requests.request(**params)
        return response

conoha_storage = ConohaStorage()


class OldConohaStorage(object):

    def __init__(self):
        self.connection = Connection(
            authurl=AUTH_URL, user=USER_NAME, auth_version=AUTH_VERSION,
            tenant_name=TENANT_NAME, key=KEY,
            os_options={'region_name': 'tyo1'}
        )

    def generate_temp_url(self, object_name, seconds=3600, method='GET'):
        signed_path = utils.generate_temp_url(
            path=STORAGE_PATH + CONTAINER + object_name,
            seconds=seconds,
            key=SIGNED_URL_KEY,
            method=method
        )

        return STORAGE_URL + signed_path

    def put_object(self, contents, filename):
        date_folder = datetime.now().strftime('/%d/%m/%Y')
        container = CONTAINER + date_folder

        try:
            self.connection.put_object(
                container,
                obj=filename,
                contents=open(contents, 'rb'),
            )
        except Exception as e:
            print("> failed to put_object: %s" % str(e))
            return {}

        return {
            'filename': filename,
            'url': config.audio.server.url + date_folder + '/' + filename
        }
