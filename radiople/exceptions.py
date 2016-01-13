# -*- coding: utf-8 -*-


class RadiopleException(Exception):

    code = '500'
    message = 'server error'
    display_message = u'서버 에러입니다.'

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            self.display_message = args[0]

        if 'code' in kwargs:
            self.code = kwargs.get('code')

        if 'message' in kwargs:
            self.message = kwargs.get('message')

        if 'display_message' in kwargs:
            self.display_message = kwargs.get('display_message')

        super()

    @property
    def data(self):
        return {
            'code': self.code,
            'message': self.message,
            'display_message': self.display_message
        }


class BadRequest(RadiopleException):

    code = '400'
    message = 'BadRequest'
    display_message = u'잘못된 요청입니다.'


class Gone(RadiopleException):

    code = '410'
    message = 'Gone'
    display_message = u'시간이 초과되었습니다.'


class Unauthorized(RadiopleException):

    code = '401'
    message = 'Unauthorized'
    display_message = u'인증되지 않은 요청입니다.'


class InvalidToken(Unauthorized):

    code = '401.001'
    display_message = u"잘못된 토큰입니다."


class ExpiredToken(Unauthorized):

    code = '401.002'
    display_message = u"토큰이 만료되었습니다."


class NotFound(RadiopleException):

    code = '404'
    message = 'Not Found'
    display_message = u'찾을 수 없습니다.'


class Conflict(RadiopleException):

    code = '409'
    message = 'Conflict'
    display_message = u'중복입니다.'


class ServerError(RadiopleException):

    code = '500'
    message = 'Server Error'
    display_message = u'서버 에러입니다.'


class ServiceUnavailable(RadiopleException):

    code = '503'
    message = 'Service Unavailable'
    display_message = u'서버 점검중입니다.'


class EntityTooLarge(RadiopleException):

    code = '413'
    message = 'Entity Too Larget'
    display_message = u'파일 사이즈가 너무 큽니다.'


class AccessDenied(RadiopleException):

    code = '403'
    message = 'Access Denied'
    display_message = u'접근할 수 없습니다.'
