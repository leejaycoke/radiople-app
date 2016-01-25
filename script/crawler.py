# -*- coding: utf-8 -*-

import os
import sys
import uuid
import re
import requests
import xmltodict

import mutagen
import feedparser

from bs4 import BeautifulSoup

from mutagen.mp3 import MP3

from pydub import AudioSegment
from pydub import utils

from dateutil import parser

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

ADMIN_USER_ID = user_service.get_admin_users()[0].id

ACCESS_TOKEN, _, _ = access_token_service.issue(
    user_id=ADMIN_USER_ID, service='console')


def convert_mp4_to_mp3(filename):
    try:
        audio = AudioSegment.from_file(filename)
        audio.export(filename, format='mp3', bitrate='128k')
    except:
        raise Exception("파일 변환이 불가능합니다. : ", filename)

    return filename


def create_default_email():
    return '%s@radiople.com' % uuid.uuid4().hex


class Broadcast(Schema):

    title = fields.String(default=None)
    link = fields.Url(default=None)
    subtitle = fields.String(default=None)
    description = fields.Method('get_summary')
    casting = fields.Method('get_casting', default=[])
    email = fields.Method('get_email')
    icon_image = fields.Method('get_icon_image')
    cover_image = fields.Method('get_cover_image')

    def get_casting(self, feed):
        castings = [c.strip() for c in feed.author.split(',')]
        for author in feed.authors:
            castings += [c.strip() for c in author.get('name').split(',')]
        return list(set(castings))

    def get_email(self, feed):
        return feed.get('author_detail', {}) \
            .get('email', create_default_email())

    def get_icon_image(self, feed):
        return feed.get('image', {}).get('href')

    def get_cover_image(self, feed):
        return feed.get('image', {}).get('href')

    def get_summary(self, feed):
        return BeautifulSoup(feed.summary, 'html.parser').text


class Episode(Schema):

    title = fields.Method('get_title')
    subtitle = fields.Method('get_subtitle')
    air_date = fields.Method('get_air_date')
    audio_url = fields.Method('get_audio_url')

    def get_title(self, entry):
        return BeautifulSoup(entry.title, 'html.parser').text

    def get_subtitle(self, entry):
        return BeautifulSoup(entry.get('subtitle', ''), 'html.parser').text

    def get_air_date(self, entry):
        return parser.parse(entry.published)

    def get_audio_url(self, entry):
        for entry in entry.links:
            link_type = entry.get('type')
            if 'audio' in link_type or 'video' in link_type:
                return entry.get('href')


class Episodes(Schema):

    episodes = fields.Nested(Episode, many=True)


class Crawler(object):

    def __init__(self, feed_url):
        self.feed_url = feed_url

    def run(self):
        feed, items = self.parse_feed()

        broadcast = broadcast_service.get_by_feed_url(self.feed_url)
        if not broadcast:
            if broadcast_service.exists_title(feed.get('title')):
                raise Exception("이미 존재하는 방송입니다. : ", feed.get('title'))

            broadcast = self.create_broadcast(feed)

        for item in items[:5]:
            if episode_service.exists_title_by_broadcast_id(
                    broadcast.id, broadcast.title):
                continue
            episode = self.create_episode(broadcast, item)
            print('> created episode : ', episode.title)

    def create_broadcast(self, feed):
        if feed['icon_image']:
            image = self.upload_image(feed['icon_image'])
        else:
            image = None

        broadcast = broadcast_service.insert(
            title=feed['title'],
            subtitle=feed['subtitle'],
            casting=feed['casting'],
            icon_image=image,
            cover_image=image,
            description=feed['description'],
            link=feed['link'],
            user_id=ADMIN_USER_ID,
            feed_url=self.feed_url
        )

        sb_broadcast_service.insert(broadcast_id=broadcast.id)

        return broadcast

    def parse_feed(self):
        content = requests.get(self.feed_url).content
        data = feedparser.parse(content)

        feed = Broadcast().dump(data.feed).data
        items = Episodes().dump({'episodes': data.entries}).data
        return feed, items.get('episodes')

    def download_file(self, url):
        filename = "/tmp/%s" % uuid.uuid4().hex

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

            sys.stdout.write('\n')
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

    def upload_audio(self, broadcast, item):
        temp_filename = self.download_file(item['audio_url'])
        try:
            audio = AudioSegment.from_file(temp_filename)
            tags = {
                'artist': broadcast.title,
                'album': broadcast.title,
                'title': item['title'],
                'comment': 'http://radiople.com',
            }
            audio.export(temp_filename, format='mp3',
                         bitrate='128k', tags=tags)
        except Exception as e:
            raise Exception("> mp3 변환 도중 에러가 발생했습니다. : ", str(e))

        try:
            mp3 = MP3(temp_filename)
        except Exception as e:
            raise Exception("> Mutagen 파일을 열 수 없습니다. : ", str(e))

        storage_service = StorageService()
        data = storage_service.put_audio(temp_filename)

        if not data:
            os.remove(temp_filename)
            raise Exception("> 업로드 도중 에러가 발생했습니다.")

        audio = audio_service.insert(
            filename=data['filename'],
            user_id=broadcast.user_id,
            upload_filename=temp_filename.split('/')[-1],
            mimes=mp3.mime,
            size=os.path.getsize(temp_filename),
            length=mp3.info.length,
            sample_rate=mp3.info.sample_rate,
            bitrate=mp3.info.bitrate,
            url=data['url']
        )

        os.remove(temp_filename)

        return audio.id

    def create_episode(self, broadcast, item):
        audio_id = self.upload_audio(broadcast, item)

        episode = episode_service.insert(
            broadcast_id=broadcast.id,
            audio_id=audio_id,
            title=item['title'],
            subtitle=item['subtitle'],
            air_date=item['air_date'],
        )

        sb_episode_service.insert(episode_id=episode.id)

        return episode


def run(args):
    crawler = Crawler(args['--feed-url'])
    crawler.run()
