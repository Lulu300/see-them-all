from inputs import Input
from urllib.parse import urljoin
from util.constants import PMS_WATCH_HISTORY, EB_NEW_SEEN_EP, bus
from functools import lru_cache
import requests
import xml.etree.ElementTree as ET
import time
import re
import logging


class Plex(Input):

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def recently_watched(self):
        logging.debug('starting recently_watched for input {0}'.format(self.name))
        history_url = urljoin(self.config.get('url'), PMS_WATCH_HISTORY)
        headers = {'X-Plex-Token': self.config.get('token')}
        response = requests.get(history_url, headers=headers)
        watched_videos = ET.fromstring(response.text).iter('Video')
        self.parse_history(watched_videos)
        logging.debug('recently_watched for input {0} finished'.format(self.name))

    def parse_history(self, watched_videos):
        for video in self.recently_watched_videos(watched_videos):
            show_id = self.get_show_id(video.get('grandparentKey'))
            if not show_id:
                continue
            episode = {
                show_id: {
                    'show_name': video.get('grandparentTitle'),
                    'season_number': video.get('parentIndex'),
                    'episode_number': video.get('index')
                }
            }
            bus.emit('{0}:{1}'.format(EB_NEW_SEEN_EP, self.name), episode)

    def recently_watched_videos(self, watched_videos):
        yda = time.time() - 24 * 60 * 60
        for v in (v for v in watched_videos if v.get('type') == 'episode'):
            if int(v.get('viewedAt')) > yda or self.config.get('sync_all'):
                yield v

    @lru_cache(maxsize=32)
    def get_show_id(self, plex_show_url):
        headers = {'X-Plex-Token': self.config.get('token')}
        show_info_url = urljoin(self.config.get('url'), plex_show_url)
        response = requests.get(show_info_url, headers=headers)
        tree = ET.fromstring(response.text)
        regex = r'com\.plexapp\.agents\.thetvdb:\/\/([^?]*)'
        content = tree.find('./Directory').get('guid')
        matches = re.findall(regex, content, re.MULTILINE)
        return matches[0] if len(matches) is 1 else False
