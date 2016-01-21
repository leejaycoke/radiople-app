# -*- coding: utf-8 -*-

from uuid import uuid4

from radiople.config import config
from swiftclient import utils
from swiftclient.client import Connection

AUTH_URL = config.common.storage.auth_url
SIGNED_URL_KEY = config.common.storage.signed_url_key
USER_NAME = config.common.storage.user_name
AUTH_VERSION = config.common.storage.auth_version
TENANT_NAME = config.common.storage.tenant_name
KEY = config.common.storage.key

STORAGE_FULL_URL = config.common.storage.full_url
STORAGE_URL = config.common.storage.url
STORAGE_PATH = config.common.storage.path


class Service(object):

    def __init__(self, container):
        self.container = container
        self.connection = Connection(
            authurl=AUTH_URL, user=USER_NAME, auth_version=AUTH_VERSION,
            tenant_name=TENANT_NAME, key=KEY
        )

    def generate_temp_url(self, object_name=None, seconds=3600, method='GET'):
        object_name = object_name or uuid4().hex

        signed_path = utils.generate_temp_url(
            path=STORAGE_PATH + self.container + '/' + object_name,
            seconds=seconds,
            key=SIGNED_URL_KEY,
            method=method
        )

        return STORAGE_URL + signed_path


class ConsoleService(Service):
    pass
