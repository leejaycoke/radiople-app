# -*- coding: utf-8 -*-

from radiople.service import Service

from radiople.model.audio_log import AudioLog


class AudioLogService(Service):

    __model__ = AudioLog


class ApiAudioLogService(AudioLogService):

    pass


service = AudioLogService()
api_service = ApiAudioLogService()
