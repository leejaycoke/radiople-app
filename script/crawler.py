# -*- coding: utf-8 -*-

import re
import sys
import time
import uuid
import random
import logging
import requests
import pytz
import json
import hashlib

import mimetypes
import mutagen
import feedparser

from urllib.parse import urlparse

from bs4 import BeautifulSoup

from datetime import datetime
from datetime import timedelta
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

TEMP_PATH = config.common.crawler.temp_path

PC_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"

ADMIN_USER_ID = user_service.get_admin_users()[0].id
ACCESS_TOKEN, _, _ = access_token_service.issue(
    user_id=ADMIN_USER_ID, service='console')

IMAGE_SERVER_URL = config.image.server.url

TIMEZONE = pytz.timezone('Asia/Seoul')


session = requests.Session()
session.headers.update({'User-Agent': PC_USER_AGENT})

URL_PATTERN = re.compile(r'^(?:http|ftp)s?://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$',
                         re.IGNORECASE | re.UNICODE)


def create_default_email():
    return '%s@radiople.com' % uuid.uuid4().hex


class Utils(object):

    @staticmethod
    def create_etag(**kwargs):
        params = {
            'broadcast_id': int(kwargs.get('broadcast_id')),
            'title': kwargs.get('title'),
            'subtitle': kwargs.get('subtitle', ''),
            'air_date': kwargs.get('air_date').strftime('%Y-%m-%d %H:%M:%S'),
            'url': kwargs.get('url'),
            'description': kwargs.get('description', '')
        }

        params = json.dumps(sorted(params.items()))

        return hashlib.md5(params.encode()).hexdigest()

    @staticmethod
    def download_file(url, retry_count=0):
        try:
            r = session.head(url, allow_redirects=True)
            if not r.ok:
                logger.error("UNKNOWN_HEAD (%d): %s", r.status_code, r.content)
                raise Exception
            info = {
                'size': int(r.headers['Content-Length']),
                'mimes': [r.headers['Content-Type']]
            }
        except Exception as e:
            if retry_count == 5:
                raise Exception(e)
            logger.debug("Retry download: %s \"%s\"", url, str(e))
            time.sleep(10)
            retry_count += 1
            return Utils.download_file(url, retry_count)

        try:
            path = urlparse(url).path
            extension = '.' + path.split('/')[-1].split('.')[-1].lower()
            if extension not in ['mp2', '.mp3', '.mp4', '.pdf']:
                extension = Utils.get_extension(info['mimes'][0])
        except Exception as e:
            print(str(e))
            extension = Utils.get_extension(info['mimes'][0])

        info['filename'] = uuid.uuid4().hex + extension
        info['full_path'] = TEMP_PATH + info['filename']

        try:
            with open(info['full_path'], "wb") as f:
                response = session.get(url, allow_redirects=True, stream=True)

                md_size = info['size'] / (1024 * 1204)
                logger.debug("Start download [%dMB]: %s", md_size, url)

                progress = 0
                for data in response.iter_content(chunk_size=2048):
                    progress += len(data)
                    f.write(data)
                    done = int(50 * progress / info['size'])
                    sys.stdout.write("\r[%s%s]" %
                                     ('=' * done, ' ' * (50 - done)))

                sys.stdout.write('\n')
                sys.stdout.flush()

            logger.debug("Complete download: %s", info['full_path'])
        except Exception as e:
            if retry_count == 5:
                raise Exception(e)
            logger.debug("Retry download: %s \"%s\"", url, str(e))
            time.sleep(10)
            retry_count += 1
            return Utils.download_file(url, retry_count)

        return info

    @staticmethod
    def is_valid_url(url):
        return URL_PATTERN.match(url)

    @staticmethod
    def get_extension(mime):
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

    @staticmethod
    def get_random_date(before_days=365):
        return datetime.now() - timedelta(days=random.randint(0, 365))


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

        # check total count
        total_count = len(items)
        count = episode_service.count_by_broadcast_id(broadcast.id)
        if total_count == count:
            logger.info("latest episode: %d", count)
            return

        for index, item in enumerate(items[:2]):
            logger.debug("total broadcast %d [%d/%d]",
                         broadcast.id, index + 1, total_count)

            etag = Utils.create_etag(broadcast_id=broadcast.id, **item)
            current = episode_service.get_by_etag(broadcast.id, etag)
            if current:
                logger.warning("already exists episode %d %s \"%s\"",
                               current.id, current.etag, current.title)
                return

            current = episode_service.get_by_url(broadcast.id, item['url'])
            if current:
                episode_service.update(current, etag=etag)
                logger.debug("update etag %s" % etag)
                continue

            if not Utils.is_valid_url(item['url']):
                logger.error("not valid url %s" % item['url'])
                continue

            logger.debug("NEW_EPISODE \"%s\" \"%s\"",
                         str(item['air_date']), item['title'])

            episode = self.create_episode(broadcast, item, etag)
            logger.info("CREATED_EPISODE %d %s \"%s\"",
                        episode.id, episode.etag, episode.title)

        latest_episode = episode_service.get_latest_episode(broadcast.id)
        broadcast_service.update(
            broadcast, latest_air_date=latest_episode.air_date)

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
            extra={'feed_url': self.feed_url}
        )

        sb_broadcast_service.insert(broadcast_id=broadcast.id)

        return broadcast

    def create_storage(self, user_id, url, air_date, retry_count=0):
        try:
            file_info = Utils.download_file(url)

            conoha_storage = ConohaStorage()
            result = conoha_storage.put_object(
                file_info['full_path'], file_info['filename'], date=air_date)

            media = Utils.get_media(file_info['full_path'])

            params = {
                'user_id': user_id,
                'filename': file_info['filename'],
                'uploaded_filename': file_info['filename'],
                'size': file_info['size'],
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
                params['mimes'] = file_info['mimes']

            return storage_service.insert(**params)
        except Exception as e:
            if retry_count == 5:
                raise Exception(e)
            retry_count += 1
            return self.create_storage(user_id, url, air_date, retry_count)

    def create_episode(self, broadcast, item, etag):
        storage = self.create_storage(broadcast.user_id, item[
                                      'url'], item['air_date'])
        logger.debug("created storage %d", storage.id)

        data = dict(
            broadcast_id=broadcast.id,
            title=item['title'],
            subtitle=item['subtitle'],
            description=item['description'],
            air_date=item['air_date'],
            storage_id=storage.id,
            extra={'url': item['url']},
            etag=etag
        )

        episode = episode_service.insert(**data)

        sb_episode_service.insert(episode_id=episode.id)

        return episode

    def upload_image(self, url):
        file_info = Utils.download_file(url)

        try:
            response = requests.put(
                IMAGE_SERVER_URL,
                params={'access_token': ACCESS_TOKEN},
                files={'file': open(file_info['full_path'], 'rb')}
            )

            return response.json().get('url')
        except Exception as e:
            return None


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
        return BeautifulSoup(feed.get('summary', ''), 'html.parser').text


class Episode(Schema):

    title = fields.Method('get_title')
    subtitle = fields.Method('get_subtitle')
    air_date = fields.Method('get_air_date')
    url = fields.Method('get_url')
    description = fields.Method('get_summary')

    def get_title(self, entry):
        return BeautifulSoup(entry.title, 'html.parser').text.strip()

    def get_subtitle(self, entry):
        return BeautifulSoup(entry.get('subtitle', ''), 'html.parser').text

    def get_air_date(self, entry):
        air_date = parser.parse(entry.published).replace(tzinfo=None)
        air_date = TIMEZONE.localize(air_date)
        return air_date

    def get_url(self, entry):
        urls = []
        for entry in entry.links:
            mime = entry.get('type')
            if mime in ['text/html']:
                continue

            if mime in ACCEPTABLE_MIMES:
                urls.append(entry.get('href'))

        if not urls:
            raise Exception("not acceptable contents")

        if len(urls) > 1:
            raise Exception("one more links exists %s" % ', '.join(urls))

        return urls[0]

    def get_summary(self, entry):
        return BeautifulSoup(entry.get('summary', ''), 'html.parser').text


class Episodes(Schema):

    episodes = fields.Nested(Episode, many=True)


def run(args):
    if args['--broadcast-id']:
        broadcast = broadcast_service.get(args['--broadcast-id'])
        if not broadcast:
            raise Exception("not exists broadcast: ", args['--broadcast-id'])
        crawler = Crawler(broadcast.extra['feed_url'])
        crawler.run()
    elif args['--feed-url']:
        crawler = Crawler(args['--feed-url'])
        crawler.run()
    else:
        broadcasts = broadcast_service.get_all()
        for broadcast in broadcasts:
            crawler = Crawler(broadcast.extra['feed_url'])
            crawler.run()
