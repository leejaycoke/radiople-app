# -*- coding: utf-8 -*-

from celery import Celery
from kombu import Queue
from kombu import Exchange

from radiople.config import config


class RadiopleTask(object):

    MAIN = 'radiople.worker.main'
    PUSH = 'radiople.worker.push'
    EMAIL = 'radiople.worker.email'
    AUDIO = 'radiople.worker.audio'


class CeleryApp(object):

    timezone = 'Asia/Seoul'
    broker_url = config.common.celery.broker_url

    def __init__(self, taskname):
        self.taskname = taskname

    @property
    def app(self):
        worker = Celery(self.taskname)
        worker.conf.update(self._config)
        return worker

    @property
    def _config(self):
        router = TaskRouter(self.taskname)
        return dict(
            CELERY_TIMEZONE=self.timezone,
            BROKER_URL=self.broker_url,
            CELERY_RESULT_BACKEND=self.broker_url,
            CELERY_TASK_RESULT_EXPIRES=3600,
            CELERY_TASK_SERIALIZER='pickle',
            CELERY_ACCEPT_CONTENT=['pickle', 'json'],
            CELERY_RESULT_SERIALIZER='json',
            CELERY_ROUTES=(router,),
            CELERY_QUEUES=(Queue(
                self.taskname, Exchange(self.taskname, type='topic'),
                routing_key='%s.#' % self.taskname),
            )
        )


class TaskRouter(object):

    def __init__(self, taskname):
        self.taskname = taskname

    def route_for_task(self, task, args=None, kwargs=None):
        return {
            'exchange': self.taskname,
            'exchange_type': 'topic',
            'routing_key': task
        }
