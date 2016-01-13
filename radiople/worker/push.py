# -*- coding: utf-8 -*-

from radiople.worker import CeleryApp
from radiople.worker import RadiopleTask

from radiople.config import config

from radiople.libs.push import PushBuilder
from radiople.libs.push import Landing
from radiople.libs.push import GCM_PER_SIZE

from radiople.service.device import service as device_service
from radiople.service.broadcast import service as broadcast_service

from gcm import GCM

worker = CeleryApp(RadiopleTask.PUSH).app


gcm = GCM(config.common.gcm.api_key)


@worker.task
def send_to_subscribers(broadcast_id):
    broadcast = broadcast_service.get(broadcast_id)
    devices = device_service.get_all_by_subsribers(broadcast_id)
    payload = PushBuilder(Landing.BROADCAST) \
        .add_param(title=broadcast.title) \
        .add_param(message="새로운 에피소드가 있습니다.") \
        .add_extra(broadcast=broadcast) \
        .build()

    push_tokens = [device.push_token for device in devices]

    send(push_tokens, payload)


@worker.task
def send_ad(broadcast_id):
    pass


@worker.task
def send(push_tokens, payload):
    push_tokens = [push_tokens[i:i + GCM_PER_SIZE]
                   for i in range(0, len(push_tokens), GCM_PER_SIZE)]

    for reg_ids in push_tokens:
        try:
            response = gcm.send_downstream_message(
                registration_ids=reg_ids, data=payload)
            process_sending_result(response)
        except:
            continue


def process_sending_result(response):
    success_keys = response.get('success')
    for success_key in success_keys.keys():
        print(">>>>> success : ", success_key)

    errors = response.get('errors')
    for error_type, error_keys in errors.items():
        pass
