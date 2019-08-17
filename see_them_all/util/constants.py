from urllib.parse import urljoin
from event_bus import EventBus


TVTIME_CLIENT_ID = 'UOWED7wBGRQv17skSZJO'
TVTIME_CLIENT_SECRET = 'ZHYcO8n8h6WbYuMDWVgXr7T571ZF_s1r1Rzu1-3B'
TVTIME_BASEURL = 'https://api.tvtime.com'
TVTIME_DEVICE_CODE = urljoin(TVTIME_BASEURL, '/v1/oauth/device/code')
TVTIME_TOKEN = urljoin(TVTIME_BASEURL, '/v1/oauth/access_token')
TVTIME_CHECKIN = urljoin(TVTIME_BASEURL, '/v1/checkin')
TVTIME_FOLLOW = urljoin(TVTIME_BASEURL, '/v1/follow')
TVTIME_WAITING_TIME = 62

SIMKL_BASEURL = 'https://api.simkl.com'
SIMKL_DEVICE_CODE = urljoin(SIMKL_BASEURL, '/oauth/pin')
SIMKL_CHECKIN = urljoin(SIMKL_BASEURL, '/sync/history')
SIMKL_RECOVER = urljoin(SIMKL_BASEURL, '/sync/all-items/?extended=full')
SIMKL_EPISODES = urljoin(SIMKL_BASEURL, '/tv/episodes/{0}')

PMS_WATCH_HISTORY = "/status/sessions/history/all"

EB_NEW_SEEN_EP = 'new:seen:episodes'

bus = EventBus()
