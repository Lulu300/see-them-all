from outputs import Output
from event_bus import EventBus
from util.constants import bus, SIMKL_BASEURL, SIMKL_CHECKIN, SIMKL_DEVICE_CODE, TVTIME_WAITING_TIME
from util.video import Video, VideoType
import os
import requests
import time
import logging
from urllib.parse import urljoin
import json

class Simkl(Output):

    def __init__(self, config):
        self.config = config
        self.token = self.get_token()

    def get_token(self):
        token = ''
        if os.path.exists(self.config.get('token_file')):
            with open(self.config.get('token_file'), 'r') as f:
                token = f.read()
        return token if len(token) > 1 else self.auth()

    def auth(self):
        device = self.request(
            method='GET',
            url=SIMKL_DEVICE_CODE,
            params={'client_id': self.config.get('client_id')}
        )

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
            r = self.request(
                    method='GET',
                    url=urljoin(SIMKL_DEVICE_CODE+'/', '{0}'.format(device['user_code'])),
                    params={'client_id': self.config.get('client_id')})
            time.sleep(device['interval'])
        print('[SIMKL] Your account has been linked.')
        with open(self.config.get('token_file'), 'w+') as f:
            f.write(r['access_token'])
        return r['access_token']

    def mark_as_watched(self, video: Video):
        if video.type_ == VideoType.EPISODE:
            self.mark_episode_as_watched(video)
        if video.type_ == VideoType.MOVIE:
            self.mark_movie_as_watched(video)

    def mark_episode_as_watched(self, video):
        r = self.request(
            method='POST',
            url=SIMKL_CHECKIN,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+self.token,
                'simkl-api-key': self.config.get('client_id'),
            },
            data=json.dumps({
                'shows': [{
                    'ids': {
                        'tvdb': int(video.ids.tvdb_id),
                    },
                    'seasons': [{
                        "number": int(video.season_number),
                        "episodes": [{
                            "number": int(video.episode_number),
                        }]
                    }]
                }]
            })
        )
        return False

    def mark_movie_as_watched(self, video):
        r = self.request(
            method='POST',
            url=SIMKL_CHECKIN,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+self.token,
                'simkl-api-key': self.config.get('client_id'),
            },
            data=json.dumps({
                'movies': [{
                    'ids': {
                        'imdb': int(video.ids.imdb_id),
                    },
                }]
            })
        )
        return False

    def request(self, url, method='GET', data={}, params={}, headers={}):
        r = requests.request(
            method=method,
            url=url,
            data=data,
            params=params,
            headers=headers,
        )
        if r.status_code is 200 or r.status_code is 201:
            return r.json()
        logging.info('Waiting 1 minute for new API slots.')
        time.sleep(TVTIME_WAITING_TIME)
        return self.request(url, method=method, data=data)
