# -*- coding: utf-8 -*-

import os
import sys
import uuid
import re
import requests
import xmltodict

from mutagen.mp3 import MP3

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
from radiople.service.audio import service as audio_service
from radiople.service.storage import Service as StorageService

PC_HEADER = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"
}

MOBILE_HEADER = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID_) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36"
}

FEED_URL_PATTERN = re.compile(r"Feed URL : <\/strong>(.+)<\/p>")

ACCESS_TOKEN, _, _ = access_token_service.issue(user_id=1, service='console')


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

        if not podbbang.broadcast_id:
            data['user_id'] = 1
            broadcast = self.create_broadcast(data)
            podbbang_service.update(podbbang, broadcast_id=broadcast.id)
        else:
            broadcast = broadcast_service.get(podbbang.broadcast_id)
            data['user_id'] = broadcast.user_id

        for episode in data.get('episodes'):
            if episode_service.get_by_broadcast_title(
                    podbbang.broadcast_id, episode['title']):
                continue

            self.create_episode(podbbang.broadcast_id,
                                broadcast.user_id, episode)

    def create_podbbang(self, feed_url):
        return podbbang_service.insert(
            id=self.channel_id,
            feed_url=feed_url
        )

    def create_broadcast(self, data):
        image = self.upload_image(data['image_url']) if data[
            'image_url'] and data['image_url'] != '' else None

        broadcast = broadcast_service.insert(
            title=data['title'],
            subtitle=data['subtitle'],
            casting=data['casting'],
            icon_image=image,
            cover_image=image,
            description=data['description'],
            link=data['link'],
            user_id=data['user_id']
        )

        sb_broadcast_service.insert(broadcast_id=broadcast.id)

        return broadcast

    def get_feed_url(self):
        try:
            html = requests.get(self.channel_url).text
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

    def download_file(self, url):
        filename = "/tmp/%s.mp3" % uuid.uuid4().hex

        with open(filename, "wb") as f:
            print("> Downloading : %s" % url)
            response = requests.get(
                url, headers=PC_HEADER, allow_redirects=True, stream=True)
            content_length = int(response.headers.get('Content-Length', 0))

            progress = 0

            for data in response.iter_content(chunk_size=1024):
                progress += len(data)
                f.write(data)
                done = int(50 * progress / content_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()

        return filename

    def upload_image(self, url):
        filename = self.download_file(url)

        url = config.image.server.url
        response = requests.put(
            url,
            params={'access_token': ACCESS_TOKEN},
            files={'file': open(filename, 'rb')}
        )
        if not response.ok:
            raise Exception(response.json().get('display_message'))

        return response.json().get('url')

    def upload_audio(self, user_id, url):
        filename = self.download_file(url)

        try:
            audio = MP3(filename)
            if audio.info.protected:
                os.remove(filename)
                sys.exit("> 에러가 발생했습니다.")
        except:
            os.remove(filename)
            sys.exit("> 에러가 발생했습니다.")

        storage_service = StorageService()
        data = storage_service.put_audio(filename)

        if not data:
            os.remove(filename)
            sys.exit("> 에러가 발생했습니다.")

        audio = audio_service.insert(
            filename=data['filename'],
            user_id=user_id,
            upload_filename=filename.split('/')[-1],
            mimes=audio.mime,
            size=os.path.getsize(filename),
            length=audio.info.length,
            sample_rate=audio.info.sample_rate,
            bitrate=audio.info.bitrate,
            url=data['url']
        )

        os.remove(filename)

        return audio.id

    def create_episode(self, broadcast_id, user_id, episode):
        audio_id = self.upload_audio(user_id, episode.get('audio_url'))

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
