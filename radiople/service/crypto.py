# -*- coding: utf-8 -*-

import hmac
import random
import pyscrypt
import msgpack

import nacl.utils
import nacl.secret

from hashlib import sha1

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

from uuid import uuid4

from dateutil.parser import parse

from base64 import b64encode
from base64 import b64decode
from base64 import urlsafe_b64encode
from base64 import urlsafe_b64decode

from datetime import datetime
from datetime import timedelta

from radiople.config import config
from radiople.common import kst_now
from radiople.common import KST_TIME_ZONE

from radiople.exceptions import InvalidToken
from radiople.exceptions import ExpiredToken


class TokenService(metaclass=ABCMeta):

    def issue(self, **kwargs):
        self.expires = kwargs.get('expires') or self.expires

        expires_at = self.create_expires_at()
        kwargs['expires_at'] = expires_at.isoformat()
        plaintext = msgpack.packb(kwargs)
        token = self.encrypt(plaintext).decode('utf-8')

        return token, expires_at, self.hash(token)

    def encrypt(self, plaintext):
        try:
            encrypted = self.box.encrypt(plaintext, self.nonce)
            return urlsafe_b64encode(encrypted)
        except:
            raise InvalidToken("잘못된 토큰값입니다.")

    def decrypt(self, token):
        try:
            return self.box.decrypt(urlsafe_b64decode(token))
        except:
            raise InvalidToken("잘못된 토큰입니다.")

    def validate(self, token, expired_ok=False):
        plaintext = self.decrypt(token)

        try:
            data = msgpack.unpackb(plaintext, encoding='utf-8')
        except:
            raise InvalidToken("잘못된 토큰입니다.")

        try:
            expires_at = parse(data['expires_at'])
        except:
            raise InvalidToken("만료일을 알 수 없는 토큰입니다.")

        if not expired_ok and self.expired(expires_at):
            raise ExpiredToken("토큰기간이 만료되었습니다.")

        self.data = data

    def expired(self, date):
        return date <= kst_now()

    def create_expires_at(self):
        offset = timedelta(**{self.expire_type: self.expires})
        return kst_now() + offset

    def hash(self, token):
        hashed = hmac.new(self.hash_key, token.encode(), sha1)
        return b64encode(hashed.digest()).decode('utf-8')

    @property
    def nonce(self):
        return nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

    @abstractproperty
    def expire_type(self):
        raise NotImplemented


class AccessTokenService(TokenService):

    secret_key = b64decode(config.common.access_token.secret_key)
    hash_key = b64decode(config.common.access_token.hash_key)
    box = nacl.secret.SecretBox(secret_key)
    expires = config.common.access_token.expires

    @property
    def expire_type(self):
        return 'days'


class ConsoleTokenService(TokenService):

    secret_key = b64decode(config.console.access_token.secret_key)
    hash_key = b64decode(config.console.access_token.hash_key)
    box = nacl.secret.SecretBox(secret_key)
    expires = config.console.access_token.expires

    @property
    def expire_type(self):
        return 'days'


class ApiTokenService(TokenService):

    secret_key = b64decode(config.api.access_token.secret_key)
    hash_key = b64decode(config.api.access_token.hash_key)
    box = nacl.secret.SecretBox(secret_key)
    expires = config.api.access_token.expires

    @property
    def expire_type(self):
        return 'days'


class EmailValidationTokenService(TokenService):

    secret_key = b64decode(config.common.email_validation.secret_key)
    hash_key = b64decode(config.common.email_validation.hash_key)
    box = nacl.secret.SecretBox(secret_key)
    expires = config.common.email_validation.expires

    @property
    def expire_type(self):
        return 'days'


class FindPasswordTokenService(TokenService):

    secret_key = b64decode(config.common.find_password.secret_key)
    hash_key = b64decode(config.common.find_password.hash_key)
    box = nacl.secret.SecretBox(secret_key)
    expires = config.common.find_password.expires

    @property
    def expire_type(self):
        return 'hours'


class PasswordService(object):

    def hash(self, password, salt=None):
        salt = salt.encode() if salt else self.create_salt()

        hashed = pyscrypt.hash(password=password.encode(),
                               salt=salt,
                               N=1024,
                               r=1,
                               p=1,
                               dkLen=128)
        return b64encode(hashed).decode('utf-8'), salt.decode('utf-8')

    def match(self, hashed_password, salt, guess_password):
        hashed, _ = self.hash(guess_password, salt)
        return hashed_password == hashed

    def create_salt(self):
        return uuid4().hex.encode()


password_service = PasswordService()
api_token_service = ApiTokenService()
console_token_service = ConsoleTokenService()
find_password_token_service = FindPasswordTokenService()
email_validation_token_service = EmailValidationTokenService()
