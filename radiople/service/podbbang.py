# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.podbbang import Podbbang


class PodbbangService(Service):

    __model__ = Podbbang

service = PodbbangService()
