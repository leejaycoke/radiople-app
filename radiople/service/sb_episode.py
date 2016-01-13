# -*- coding: utf-8 -*-

from dateutil.parser import parse as parse_date

from radiople.db import Session
from radiople.service import Service

from radiople.model.sb_episode import SbEpisode

from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.orm import joinedload


class SbEpisodeService(Service):

    __model__ = SbEpisode


class ApiSbEpisodeService(SbEpisodeService):

    pass


class ConsoleSbEpisodeService(SbEpisodeService):

    pass


service = SbEpisodeService()
api_service = ApiSbEpisodeService()
console_service = ConsoleSbEpisodeService()
