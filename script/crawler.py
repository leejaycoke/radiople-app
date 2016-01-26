# -*- coding: utf-8 -*-

import sys
import uuid
import logging
import requests

import mimetypes
import mutagen
import feedparser

from bs4 import BeautifulSoup

from pydub import AudioSegment

from dateutil import parser

from marshmallow import fields
from marshmallow import Schema

from radiople.libs.conoha import ConohaStorage

from radiople.config import config

from radiople.model.storage import ACCEPTABLE_MIMES

from radiople.service.crypto import access_token_service
from radiople.service.user import service as user_service
from radiople.service.broadcast import service as broadcast_service
from radiople.service.sb_broadcast import service as sb_broadcast_service
from radiople.service.episode import service as episode_service
from radiople.service.sb_episode import service as sb_episode_service
from radiople.service.storage import service as storage_service


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
stream.setFormatter(formatter)
logger.addHandler(stream)

TEMP_PATH = '/tmp/'

PC_HEADER = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"
}

ADMIN_USER_ID = user_service.get_admin_users()[0].id
ACCESS_TOKEN, _, _ = access_token_service.issue(
    user_id=ADMIN_USER_ID, service='console')

IMAGE_SERVER_URL = config.image.server.url


def convert_mp4_to_mp3(filename):
    try:
        audio = AudioSegment.from_file(filename)
        audio.export(filename, format='mp3', bitrate='128k')
    except:
        raise Exception("파일 변환이 불가능합니다. : ", filename)

    return filename


def create_default_email():
    return '%s@radiople.com' % uuid.uuid4().hex


class Utils(object):

    @staticmethod
    def download_file(url, filename):
        info = {
            'filename': Utils.get_filename(filename)
        }

        with open(filename, "wb") as f:
            response = requests.get(
                url, headers=PC_HEADER, allow_redirects=True, stream=True)

            content_length = int(response.headers.get('Content-Length', 0))
            info['size'] = content_length

            md_size = content_length / (1024 * 1204)
            logger.debug("Start download [%dMB]: %s", md_size, url)

            progress = 0
            for data in response.iter_content(chunk_size=1024):
                progress += len(data)
                f.write(data)
                done = int(50 * progress / content_length)
                sys.stdout.write("\r[%s%s]" %
                                 ('=' * done, ' ' * (50 - done)))

            sys.stdout.write('\n')
            sys.stdout.flush()

        logger.debug("Complete download: %s", filename)

        return info

    @staticmethod
    def get_extension(mime, url):
        guess_mime = mimetypes.guess_type(url)
        if guess_mime:
            extension = mimetypes.guess_extension(guess_mime[0])
            if not extension:
                return '.' + guess_mime[0].split('/')[-1]
        else:
            extension = mimetypes.guess_extension(mime)
            if not extension:
                return '.' + mime.split('/')[-1]
        return extension

    @staticmethod
    def get_media(filename):
        try:
            media = mutagen.File(filename)
            if hasattr(media, 'info'):
                return media
            else:
                logger.warning("NOT_FOUND_MEDIA_INFO %s", filename)
                raise Exception("not media file")
        except:
            logger.warning("NOT_MEDIA_FILE %s", filename)
            return None

    @staticmethod
    def get_filename(full_filename):
        return full_filename.split('/')[-1]

    @staticmethod
    def generate_filename(extension):
        return '%s%s%s' % (TEMP_PATH, uuid.uuid4().hex, extension)


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
            if 'name' in author:
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
    content = fields.Method('get_content')

    def get_title(self, entry):
        return BeautifulSoup(entry.title, 'html.parser').text.strip()

    def get_subtitle(self, entry):
        return BeautifulSoup(entry.get('subtitle', ''), 'html.parser').text

    def get_air_date(self, entry):
        return parser.parse(entry.published)

    def get_content(self, entry):
        for entry in entry.links:
            mime = entry.get('type')
            if mime in ACCEPTABLE_MIMES:
                return {'url': entry.get('href'), 'mime': mime}
            else:
                logging.warning("NOT_ACCEPTABLE_CONTENT: %s", mime)


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
                logger.error("Already exists broadcast: %s", feed.get('title'))
                sys.exit(1)

            logger.info("Create broadcast: %s", feed.get('title'))
            broadcast = self.create_broadcast(feed)

        for item in items[:30]:
            if episode_service.exists_title_by_broadcast_id(
                    broadcast.id, item['title']):
                logger.warning("ALREADY_EXISTS_EPISODE \"%s\"", item['title'])
                continue

            storage = self.create_storage(broadcast.user_id, item['content'])
            logger.info("CREATED_STORAGE %d", storage.id)
            episode = self.create_episode(broadcast.id, storage.id, item)
            logger.info("CREATED_EPISODE %d", episode.id)

    def parse_feed(self):
        content = requests.get(self.feed_url).content
        data = feedparser.parse(content)

        feed = Broadcast().dump(data.feed).data
        items = Episodes().dump({'episodes': data.entries}).data
        return feed, items.get('episodes')

    def create_broadcast(self, feed):
        if feed['icon_image']:
            image = self.upload_image(feed['icon_image'])
        else:
            print(">>>>>>>>>>>> no image")
            image = None

        broadcast = broadcast_service.insert(
            title=feed['title'],
            subtitle=feed['subtitle'],
            casting=feed['casting'],
            icon_image=image,
            cover_image=image,
            description=feed['description'],
            link=feed.get('link'),
            user_id=ADMIN_USER_ID,
            feed_url=self.feed_url
        )

        sb_broadcast_service.insert(broadcast_id=broadcast.id)

        return broadcast

    def create_storage(self, user_id, content):
        extension = Utils.get_extension(**content)
        filename = Utils.generate_filename(extension)
        data = Utils.download_file(content['url'], filename)

        conoha_storage = ConohaStorage()
        # upload filename, saving filename
        result = conoha_storage.put_object(filename, data['filename'])

        media = Utils.get_media(filename)

        params = {
            'user_id': user_id,
            'filename': data['filename'],
            'uploaded_filename': data['filename'],
            'size': data['size'],
            'url': result['url']
        }

        if media is not None:
            params['mimes'] = media.mime
            params['extra'] = {
                'bitrate': media.info.bitrate,
                'sample_rate': media.info.sample_rate,
                'length': media.info.length
            }
        else:
            params['mimes'] = [content['mime']]

        return storage_service.insert(**params)

    def create_episode(self, broadcast_id, storage_id, item):
        episode = episode_service.insert(
            broadcast_id=broadcast_id,
            title=item['title'],
            subtitle=item['subtitle'],
            air_date=item['air_date'],
            storage_id=storage_id
        )

        sb_episode_service.insert(episode_id=episode.id)

        return episode

    def upload_image(self, url):
        extension = Utils.get_extension(mime='image/jpeg', url=url)
        filename = Utils.generate_filename(extension)
        Utils.download_file(url, filename)

        try:
            response = requests.put(
                IMAGE_SERVER_URL,
                params={'access_token': ACCESS_TOKEN},
                files={'file': open(filename, 'rb')}
            )

            return response.json().get('url')
        except:
            return None


def run(args):
    crawler = Crawler(args['--feed-url'])
    crawler.run()
