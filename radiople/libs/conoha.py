# -*- coding: utf-8 -*-

import uuid

from datetime import datetime

from swiftclient import utils
from swiftclient.client import Connection

from radiople.config import config


AUTH_URL = config.common.storage.auth_url
SIGNED_URL_KEY = config.common.storage.signed_url_key
USER_NAME = config.common.storage.user_name
AUTH_VERSION = config.common.storage.auth_version
TENANT_NAME = config.common.storage.tenant_name
KEY = config.common.storage.key

STORAGE_FULL_URL = config.common.storage.full_url
STORAGE_URL = config.common.storage.url
STORAGE_PATH = config.common.storage.path

CONTAINER = config.common.storage.container


class ConohaStorage(object):

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
