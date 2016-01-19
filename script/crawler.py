# -*- coding: utf-8 -*-

import uuid
import re
import requests
import xmltodict

from datetime import datetime

from marshmallow import fields
from marshmallow import Schema

from radiople.model.role import Role

from radiople.libs.permission import Service

from radiople.config import config

from radiople.service.crypto import access_token_service
from radiople.service.podbbang import service as podbbang_service
from radiople.service.user import service as user_service
from radiople.service.sb_user import service as sb_user_service
from radiople.service.broadcast import service as broadcast_service
from radiople.service.sb_broadcast import service as sb_broadcast_service
from radiople.service.episode import service as episode_service
from radiople.service.sb_episode import service as sb_episode_service
from radiople.service.user_broadcast import service as user_broadcast_service
from radiople.service.setting import service as setting_service

PC_HEADER = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"
}

MOBILE_HEADER = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID_) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36"
}

FEED_URL_PATTERN = re.compile(r"Feed URL : <\/strong>(.+)<\/p>")


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
    casting = fields.Method('get_casting', default=[])
    email = fields.Method('get_email')
    image_url = fields.Method('get_image_url')

    episodes = fields.Nested(Episode, many=True, attribute='item')

    def get_casting(self, channel):
        casting = channel.get('itunes:author', '')
        if casting:
            return [c.strip() for c in casting.split(',')]
        return []

    def get_email(self, channel):
        return channel.get('itunes:owner', {}).get('itunes:email')

    def get_image_url(self, channel):
        return channel.get('itunes:image', {}).get('@href')


class Crawler(object):

    FEED_URL_PATTERN = re.compile(r"Feed URL : <\/strong>(.+)<\/p>")

    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.channel_url = "http://podbbang.com/ch/%d" % channel_id

    def run(self):
        podbbang = podbbang_service.get(self.channel_id)
        if not podbbang:
            feed_url = self.get_feed_url()
            podbbang = self.create_podbbang(feed_url)

        data = self.parse_feed(podbbang.feed_url)

        if podbbang.broadcast_id:
            user_broadcast = user_broadcast_service.get_by_broadcast_id(
                podbbang.broadcast_id)
            self.issue_access_token(user_broadcast.user_id)
        else:
            user = self.create_user()
            self.issue_access_token(user.id)
            broadcast = self.create_broadcast(data)

            self.create_user_broadcast(user.id, broadcast.id)
            podbbang_service.update(podbbang, broadcast_id=broadcast.id)

        broadcast_id = podbbang.broadcast_id

        for episode in data.get('episodes'):
            if episode_service.guess_exists_episode(
                    broadcast_id, episode['title'], episode['air_date']):
                continue

            self.create_episode(podbbang.broadcast_id, episode)

    def create_podbbang(self, feed_url):
        return podbbang_service.insert(
            id=self.channel_id,
            feed_url=feed_url
        )

    def create_broadcast(self, data):
        image = self.upload_image(data['image_url'], is_url=True) if data[
            'image_url'] else None

        broadcast = broadcast_service.insert(
            title=data['title'],
            subtitle=data['subtitle'],
            casting=data['casting'],
            icon_image=image,
            cover_image=image,
            description=data['description'],
            link=data['link']
        )

        sb_broadcast_service.insert(broadcast_id=broadcast.id)

        return broadcast

    def get_feed_url(self):
        try:
            html = requests.get(self.channel_url).content
            print(">>>>>>>>>>>>>>>>>>>>>>>", type(html))
        except:
            raise Exception("failed to networking: ", self.channel_url)

        try:
            return self.FEED_URL_PATTERN.findall(html)[0]
        except:
            raise Exception("failed to parsing xml url")

    def parse_feed(self, feed_url):
        content = requests.get(feed_url).content
        data = xmltodict.parse(content)

        rss = data.get('rss')
        channel = rss.get('channel')

        return Broadcast().dump(channel).data

    def create_user(self):
        user = user_service.insert(
            email=uuid.uuid4().hex + "@radiople.com",
            nickname=uuid.uuid4().hex,
            role=Role.DJ
        )

        sb_user_service.insert(
            user_id=user.id
        )

        setting_service.insert(
            user_id=user.id
        )

        return user

    def create_user_broadcast(self, user_id, broadcast_id):
        return user_broadcast_service.insert(
            user_id=user_id, broadcast_id=broadcast_id)

    def download_image(self, image_url):
        image = requests.get(image_url, headers=PC_HEADER,
                             allow_redirects=True, stream=True)
        return image.raw

    def upload_image(self, image, is_url=False):
        if is_url:
            image = self.download_image(image)

        url = config.image.server.url
        response = requests.put(
            url,
            params={'access_token': self.access_token},
            files={'file': image}
        )

        return response.json().get('url')

    def download_audio(self, audio_url):
        audio = requests.get(audio_url, headers=PC_HEADER,
                             allow_redirects=True, stream=True)
        return audio.raw

    def upload_audio(self, audio, is_url=False):
        if is_url:
            audio = self.download_audio(audio)

        url = config.audio.server.url
        response = requests.put(
            url,
            params={'access_token': self.access_token},
            files={'file': audio}
        )

        return response.json().get('id')

    def issue_access_token(self, user_id):
        self.access_token, _, _ = access_token_service.issue(
            user_id=user_id, service=Service.API)

    def create_episode(self, broadcast_id, episode):
        audio_id = self.upload_audio(episode.get('audio_url'), is_url=True)
        episode = episode_service.insert(
            broadcast_id=broadcast_id,
            audio_id=audio_id,
            title=episode['title'],
            subtitle=episode['subtitle'],
            air_date=episode['air_date'],
        )

        sb_episode_service.insert(episode_id=episode.id)

        return episode


def run(args):
    crawler = Crawler(int(args['--channel-id']))
    crawler.run()
