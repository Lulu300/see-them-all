from urllib.parse import urljoin
from event_bus import EventBus


TVTIME_CLIENT_ID = 'UOWED7wBGRQv17skSZJO'
TVTIME_CLIENT_SECRET = 'ZHYcO8n8h6WbYuMDWVgXr7T571ZF_s1r1Rzu1-3B'
TVTIME_BASEURL = 'https://api.tvshowtime.com'
TVTIME_DEVICE_CODE = urljoin(TVTIME_BASEURL, '/v1/oauth/device/code')
TVTIME_TOKEN = urljoin(TVTIME_BASEURL, '/v1/oauth/access_token')
TVTIME_CHECKIN = urljoin(TVTIME_BASEURL, '/v1/checkin')
TVTIME_FOLLOW = urljoin(TVTIME_BASEURL, '/v1/follow')

PMS_WATCH_HISTORY = "/status/sessions/history/all"

EB_NEW_SEEN_EP = 'new:seen:episodes'

bus = EventBus()
