# -*- coding: utf-8 -*-

from radiople.worker import CeleryApp
from radiople.worker import RadiopleTask

worker = CeleryApp(RadiopleTask.AUDIO).app


@worker.task
def conver_audio(from_format, to_format):
    pass
