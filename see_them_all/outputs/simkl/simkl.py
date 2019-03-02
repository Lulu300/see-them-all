from outputs import Output
from event_bus import EventBus
from urllib.parse import urljoin
from util.constants import bus, SIMKL_BASEURL, SIMKL_CHECKIN, SIMKL_DEVICE_CODE, TVTIME_WAITING_TIME
from util.video import Video, VideoType
from requests import request
import os
import time
import logging
import json


class Simkl(Output):

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

    def mark_as_watched(self, videos):
        videos_watched = {
            'shows': list(),
            'movies': list()
        }
        shows = dict()
        for video in videos:
            if video.type_ == VideoType.EPISODE:
                existing_show = shows.get(video.ids.tvdb_id, None)
                if existing_show is None:
                    existing_show = dict()
                existing_season = existing_show.get(video.season_number, None)
                if existing_season is None:
                    existing_season = list()
                existing_season.append({'number': video.episode_number})
                existing_show[video.season_number] = existing_season
                shows[video.ids.tvdb_id] = existing_show
            if video.type_ == VideoType.MOVIE:
                movie = {
                    'ids': {
                        'imdb': video.ids.imdb_id
                    }
                }
                videos_watched['movies'].append(movie)
        for show_id, show in shows.items():
            videos = {
                'ids': {
                    'tvdb': show_id
                },
                'seasons': list()
            }
            for season_number, episodes in show.items():
                videos['seasons'].append({
                    'number': season_number,
                    'episodes': episodes
                })
            videos_watched['shows'].append(videos)
        self.mark_videos_as_watched(videos_watched)     

    def mark_videos_as_watched(self, videos):
        r = request(
            method='POST',
            url=SIMKL_CHECKIN,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {0}'.format(self.token),
                'simkl-api-key': self.config.get('client_id'),
            },
            data=json.dumps(videos)
        )
        if r.status_code < 200 or r.status_code > 399:
            logging.error('Cannot mark as watch your videos with message {0}'.format(r.text))
        r_json = r.json()
        failed_shows = r_json.get('not_found').get('shows')
        failed_movies = r_json.get('not_found').get('movies')
        if len(failed_shows) + len(failed_movies) > 0:
            logging.warning('Successfully mark all your videos as watched except for {0} videos'.format(len(failed_shows) + len(failed_movies)))
        else:
            logging.debug('Successfully mark all your videos as watched')
        return True

    def write_cache_to_file():
        pass
