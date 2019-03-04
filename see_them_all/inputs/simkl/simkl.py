from inputs import Input
from urllib.parse import urljoin
from util.constants import PMS_WATCH_HISTORY, EB_NEW_SEEN_EP, bus, SIMKL_RECOVER, SIMKL_EPISODES
from util.video import Video, VideoType, VideoSchema
from joblib import Memory
import requests
import xml.etree.ElementTree as ET
import time
import re
import logging
import os
import discord
import json
from requests import request
from util.video import Video, VideoType
import sys


class Simkl(Input):

    def __init__(self, name, config, cache_folder):
        self.name = name
        self.config = config
        self.cache_folder = cache_folder
        self.token = self.get_token()

    def get_token(self):
        token = ''
        if os.path.exists(self.config.get('token_file')):
            with open(self.config.get('token_file'), 'r') as f:
                token = f.read()
        return token if len(token) > 1 else self.auth()

    def auth(self):
        device = request(
            method='GET',
            url=SIMKL_DEVICE_CODE,
            params={'client_id': self.config.get('client_id')}
        ).json()

        r = {}
        r['result'] = 'KO'
        print(
            '[SIMKL] Linking with your SIMKL account using the code {0}.'
            .format(device['device_code'])
        )
        print(
            '[SIMKL] Please open the URL {0} in your browser.'
            .format(device['verification_url'])
        )
        print('[SIMKL] Connect with your SIMKL account and '
              'type in the following code :')
        print('[SIMKL] {0}'.format(device['user_code']))
        print('[SIMKL] Waiting for you to type in the code in SIMKL.')
        while r['result'] != 'OK':
            r = request(
                    method='GET',
                    url=urljoin(SIMKL_DEVICE_CODE+'/', '{0}'.format(device['user_code'])),
                    params={'client_id': self.config.get('client_id')}).json()
            time.sleep(device['interval'])
        print('[SIMKL] Your account has been linked.')
        with open(self.config.get('token_file'), 'w+') as f:
            f.write(r['access_token'])
        return r['access_token']

    def recently_watched(self):
        r = request(
            method='GET',
            url=SIMKL_RECOVER,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {0}'.format(self.token),
                'simkl-api-key': self.config.get('client_id'),
            }
        )
        if r.status_code < 200 or r.status_code > 399:
            logging.error('Cannot retrieve your videos with message {0}'.format(r.text))
        r_json = r.json()

        videos = []
        for show in r_json.get('shows')+r_json.get('anime'):
            if show.get('seasons', None) is None:
                seasons = request(
                    method='GET',
                    url=SIMKL_EPISODES.format(show.get('show').get('ids').get('simkl')),
                    params={'client_id': self.config.get('client_id')}
                ).json()
                max_season = sys.maxsize
                max_episode = sys.maxsize
                if show.get('next_to_watch') is not None:
                    max_season, max_episode = (int(x) for x in show.get('last_watched')[1:].split('E'))
                for episode in seasons:
                    if episode.get('season', None) is not None:
                        if episode.get('season') <= max_season and episode.get('episode') <= max_episode:
                            videos.append(Video(
                                show.get('show').get('title'), VideoType.EPISODE,
                                Video.Id(imdb_id=str(show.get('show').get('ids').get('imdb')),
                                tmdb_id=int(show.get('show').get('ids').get('tmdb')),
                                tvdb_id=str(show.get('show').get('ids').get('tvdb'))),
                                episode.get('season'), episode.get('episode'),
                            ))
            else:
                for season in show.get('seasons', []):
                    for episode in season.get('episodes', []):
                        videos.append(Video(
                            show.get('show').get('title'), VideoType.EPISODE,
                            Video.Id(imdb_id=str(show.get('show').get('ids').get('imdb')),
                            tmdb_id=int(show.get('show').get('ids').get('tmdb')),
                            tvdb_id=str(show.get('show').get('ids').get('tvdb'))),
                            season.get('number'), episode.get('number'),
                        ))
        for movie in r_json.get('movies'):
            videos.append(Video(
                movie.get('movie').get('title'), VideoType.MOVIE,
                Video.Id(imdb_id=str(movie.get('movie').get('ids').get('imdb')),
                tmdb_id=int(movie.get('movie').get('ids').get('tmdb')),
                tvdb_id=str(movie.get('movie').get('ids').get('tvdb'))),
            ))
        bus.emit('{0}:{1}'.format(EB_NEW_SEEN_EP, self.name), videos)
