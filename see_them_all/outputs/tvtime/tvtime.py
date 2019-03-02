from outputs import Output
from event_bus import EventBus
from util.constants import bus, TVTIME_BASEURL, TVTIME_CHECKIN, TVTIME_CLIENT_ID, TVTIME_CLIENT_SECRET, TVTIME_DEVICE_CODE, TVTIME_FOLLOW, TVTIME_TOKEN, TVTIME_WAITING_TIME
from util.video import Video, VideoType
import os
import requests
import time
import logging


class Tvtime(Output):

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
            method='POST',
            url=TVTIME_DEVICE_CODE,
            data={'client_id': TVTIME_CLIENT_ID}
        )

        r = {}
        r['result'] = 'KO'
        print(
            '[TVTIME] Linking with your TVTime account using the code {0}.'
            .format(device['device_code'])
        )
        print(
            '[TVTIME] Please open the URL {0} in your browser.'
            .format(device['verification_url'])
        )
        print('[TVTIME] Connect with your TVTime account and '
              'type in the following code :')
        print('[TVTIME] {0}'.format(device['user_code']))
        print('[TVTIME] Waiting for you to type in the code in TVShowTime.')
        while r['result'] != 'OK':
            r = self.request(
                    method='POST',
                    url=TVTIME_TOKEN,
                    data={'client_id': TVTIME_CLIENT_ID,
                          'client_secret': TVTIME_CLIENT_SECRET,
                          'code': device['device_code']})
            time.sleep(device['interval'])
        print('[TVTIME] Your account has been linked.')
        with open(self.config.get('token_file'), 'w+') as f:
            f.write(r['access_token'])
        return r['access_token']

    def mark_as_watched(self, video: Video):
        self.follow(video.ids.tvdb_id, video.title)
        self.mark_episode_as_watched(video)

    def follow(self, show_id, show_name):
        r = self.request(
            method='POST',
            url=TVTIME_FOLLOW,
            data={'access_token': self.token,
                  'show_id': show_id})
        if r['result'] == 'OK':
            logging.info('Follow {0}.'.format(show_name))
            return True
        logging.warning(
            'Cannot Follow {0} with message : {1}.'
            .format(show_name, r['message'])
        )
        return False

    def mark_episode_as_watched(self, video):
        r = self.request(
            method='POST',
            url=TVTIME_CHECKIN,
            data={
                'access_token': self.token,
                'show_id': video.ids.tvdb_id,
                'season_number': video.season_number,
                'number': video.episode_number
            }
        )
        if r['result'] == 'OK':
            logging.info(
                'Mark as watched {0} season {1} episode {2}'
                .format(
                    video.title,
                    video.season_number,
                    video.episode_number
                )
            )
            return True
        logging.warning(
            'Cannot mark as watched {0} season {1} episode {2} with message : {3}.'
            .format(
                video.title,
                video.season_number,
                video.episode_number,
                r['message']
            )
        )
        return False

    def request(self, url, method='GET', data={}, params={}):
        r = requests.request(
            method=method,
            url=url,
            data=data,
            params=params,
        )
        if r.status_code is 200:
            return r.json()
        logging.info('Waiting 1 minute for new API slots.')
        time.sleep(TVTIME_WAITING_TIME)
        return self.request(url, method=method, data=data)
