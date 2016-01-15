# -*- coding: utf-8 -*-

import uuid

import re

from datetime import datetime

import requests

import xmltodict
from marshmallow import fields
from marshmallow import Schema

from radiople.config import config

from radiople.service.podbbang import service as podbbang_service
from radiople.service.user import service as user_service
from radiople.service.sb_user import service as sb_user_service
from radiople.service.user_auth import service as user_auth_service
from radiople.service.broadcast import service as broadcast_service
from radiople.service.sb_broadcast import service as sb_broadcast_service
from radiople.service.episode import service as episode_service
from radiople.service.sb_episode import service as sb_episode_service
from radiople.service.user_broadcast import service as user_broadcast_service
from radiople.service.setting import service as setting_service

ACCESS_TOKEN = "urA1ioj1T2UqjyZWYKP4yNhjbh5w5XvcuCTxkEkaaAQvHHVDbgIpfo0IBtGdj-4_5Ll48LoCj_QmvTgG1Gm_wztrEQQbDtNRiK2BvZbHrA73xtbjbY8JqOlp_dBSobwWxZY="

PC_HEADER = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"
}

MOBILE_HEADER = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID_) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36"
}

FEED_URL_PATTERN = re.compile(
    r'"(http:\/\/pod\.ssenhosting\.com\/rss\/.+\/?.+\.xml?)"')

CHANNEL_URL = "http://m.podbbang.com/ch/{channel_id}"


def create_podbbang(channel_id):
    channel = get_channel(channel_id)
    if not channel:
        raise Exception("%d is not exists channel id in podbbang" % channel_id)

    feed_url = get_feed_url(channel)

    return podbbang_service.insert(id=channel_id, feed_url=feed_url)


def get_channel(channel_id):
    url = CHANNEL_URL.format(channel_id=channel_id, headers=MOBILE_HEADER)

    try:
        response = requests.get(url)
        if not response.ok:
            raise Exception("response is not ok for getting channel xml")
    except Exception as e:
        raise(e)

    return response.text


def get_feed_url(channel):
    try:
        matches = re.findall(FEED_URL_PATTERN, channel)
        return matches[0]
    except:
        raise Exception("failed to parsing feed_url")


def parse(content):
    content = xmltodict.parse(content)
    rss = content.get('rss')
    channel = rss.get('channel')

    return Broadcast().dump(channel).data


def get_feed(url):
    content = requests.get(url, headers=PC_HEADER).content
    return parse(content)


def create_broadcast(podbbang):
    data = get_feed(podbbang.feed_url)
    if data['image_url']:
        data['image_url'] = upload_image(data['image_url'], is_url=True)

    broadcast = broadcast_service.insert(
        title=data['title'],
        subtitle=data['subtitle'],
        casting=data['casting'],
        icon_image=data['image_url'],
        cover_image=data['image_url'],
        description=data['description'],
        link=data['link']
    )

    sb_broadcast_service.insert(broadcast_id=broadcast.id)

    podbbang_service.update(podbbang, broadcast_id=broadcast.id)

    return broadcast


def create_episode(broadcast, user_id, broadcast_id, episode):
    audio_id = upload_audio(user_id, episode.get('audio_url'), is_url=True)
    episode = episode_service.insert(
        broadcast_id=broadcast_id,
        audio_id=audio_id,
        title=episode['title'],
        subtitle=episode['subtitle'],
        air_date=episode['air_date'],
    )

    sb_episode_service.insert(episode_id=episode.id)

    broadcast_service.update(broadcast, latest_air_date=episode.air_date)

    return episode


def create_user(email, nickname, broadcast_id):
    if not email:
        email = uuid.uuid4().hex + '@radiople.com'

    user = user_service.insert(
        email=email,
        nickname=nickname,
        broadcast_id=broadcast_id
    )

    sb_user_service.insert(user_id=user.id)

    setting_service.insert(user_id=user.id)

    user_auth_service.insert(user_id=user.id, password=1, salt=1)

    return user


def exists_episode(broadcast_id, title, air_date):
    return episode_service.guess_exists_episode(broadcast_id, title, air_date)


def create_user_broadcast(user_id, broadcast_id):
    return user_broadcast_service.insert(user_id=user_id, broadcast_id=broadcast_id)


def run(args):
    channel_id = args['--channel-id']
    podbbang = podbbang_service.get(int(args['--channel-id']))
    if not podbbang:
        podbbang = create_podbbang(channel_id)

    if not podbbang.broadcast_id:
        broadcast = create_broadcast(podbbang)
    else:
        broadcast = broadcast_service.get(podbbang.broadcast_id)

    data = get_feed(podbbang.feed_url)
    data.get('episodes')

    user = user_service.get_by_email(data.get('email'))
    if not user:
        user = create_user(data.get('email'), data.get(
            'casting')[0], podbbang.broadcast_id)
        create_user_broadcast(user.id, broadcast.id)
    else:
        if not user_broadcast_service.exists(user.id, broadcast.id):
            create_user_broadcast(user.id, broadcast.id)

    broadcast_id = broadcast.id
    user_id = user.id

    for episode in data.get('episodes')[:25]:
        if exists_episode(broadcast_id, episode['title'], episode['air_date']):
            continue
        create_episode(broadcast, user_id, broadcast_id, episode)


def download_audio(audio_url):
    audio = requests.get(audio_url, headers=PC_HEADER,
                         allow_redirects=True, stream=True)
    return audio.raw


def upload_audio(user_id, audio, is_url=False):
    if is_url:
        audio = download_audio(audio)

    url = config.audio.server.url
    response = requests.put(url,
                            params={
                                'service': 'api',
                                'access_token': ACCESS_TOKEN
                            },
                            files={'file': audio})

    return response.json().get('id')


def download_image(image_url):
    image = requests.get(image_url, headers=PC_HEADER,
                         allow_redirects=True, stream=True)
    return image.raw


def upload_image(image, is_url=False):
    if is_url:
        image = download_image(image)

    url = config.image.server.url
    response = requests.put(
        url,
        params={
            'service': 'api',
            'access_token': ACCESS_TOKEN
        },
        files={'file': image}
    )

    return response.json().get('url')


class Episode(Schema):

    title = fields.String(default=None)
    subtitle = fields.String(default=None, attribute='itunes:subtitle')
    air_date = fields.Method('get_air_date')
    audio_url = fields.Url(attribute='guid')

    def get_air_date(self, episode):
        return datetime.strptime(
            episode.get('pubDate'), "%a, %d %b %Y %H:%M:%S %z")


class Broadcast(Schema):

    title = fields.String(default=None)
    link = fields.Url(default=None)
    subtitle = fields.String(default=None, attribute='itunes:subtitle')
    description = fields.String(default=None)
    casting = fields.Method('get_casting')
    email = fields.Method('get_email')
    image_url = fields.Method('get_image_url')

    episodes = fields.Nested(Episode, many=True, attribute='item')

    def get_casting(self, channel):
        casting = channel.get('itunes:author', '').split(',')
        return [c.strip() for c in casting]

    def get_email(self, channel):
        return channel.get('itunes:owner', {}).get('itunes:email')

    def get_image_url(self, channel):
        return channel.get('itunes:image', {}).get('@href')
