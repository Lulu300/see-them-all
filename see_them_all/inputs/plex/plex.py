from inputs import Input
from urllib.parse import urljoin
from util.constants import PMS_WATCH_HISTORY, EB_NEW_SEEN_EP, bus
from util.video import Video, VideoType
from joblib import Memory
import requests
import xml.etree.ElementTree as ET
import time
import re
import logging
import os


class Plex(Input):

    def __init__(self, name, config, cache_folder):
        self.name = name
        self.config = config
        self.cache_folder = cache_folder
        self.memory = Memory(os.path.join(self.cache_folder, name), bytes_limit=1000000)
        self.get_show_id = self.memory.cache(self.get_show_id, ignore=['self'])

    def recently_watched(self):
        logging.debug('starting recently_watched for input {0}'.format(self.name))
        history_url = urljoin(self.config.get('url'), PMS_WATCH_HISTORY)
        headers = {'X-Plex-Token': self.config.get('token')}
        response = requests.get(history_url, headers=headers)
        watched_videos = ET.fromstring(response.text)
        self.parse_history(watched_videos)
        logging.debug('recently_watched for input {0} finished'.format(self.name))

    def parse_history(self, watched_videos):
        videos = []
        for video in self.recently_watched_videos(watched_videos):
            if video.get('type') == 'episode':
                tvdb_id = self.get_show_id(video.get('grandparentKey'), 'thetvdb')
                if not tvdb_id:
                    continue
                v = Video(
                    video.get('grandparentTitle'), VideoType.EPISODE,
                    video.get('parentIndex'), video.get('index'), tvdb_id=tvdb_id
                )
            if video.get('type') == 'movie':
                imdb_id = self.get_show_id(video.get('key'), 'imdb')
                if not imdb_id:
                    continue
                v = Video(
                    video.get('title'), VideoType.MOVIE, imdb_id=imdb_id
                )
            videos.append(v)
        bus.emit('{0}:{1}'.format(EB_NEW_SEEN_EP, self.name), videos)

    def recently_watched_videos(self, watched_videos):
        yda = time.time() - 24 * 60 * 60
        video_types = self.config.get('video_types')
        for v in (v for v in watched_videos if v.get('type') in video_types):
            if int(v.get('viewedAt')) > yda or self.config.get('sync_all'):
                for user in v.iterfind('User'):
                    if user.get('title') in self.config.get('users'):
                        yield v

    def get_show_id(self, plex_show_url, agent):
        if plex_show_url is None:
            logging.warning('Cannot find video info, probably because you remove it or it\'s not sync with tvdb/imdb database')
            return False
        headers = {'X-Plex-Token': self.config.get('token')}
        show_info_url = urljoin(self.config.get('url'), plex_show_url)
        response = requests.get(show_info_url, headers=headers)
        tree = ET.fromstring(response.text)
        regex = r'com\.plexapp\.agents\.{0}:\/\/([^?]*)'.format(agent)
        if agent == 'thetvdb':
            content = tree.find('./Directory').get('guid')
        else:
            content = tree.find('./Video').get('guid')
        matches = re.findall(regex, content, re.MULTILINE)
        return matches[0] if len(matches) is 1 else False
