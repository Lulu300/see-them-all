from inputs import Input
from event_bus import EventBus
from util.constants import bus

# bus = EventBus()


class Plex(Input):

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def recently_watched(self):
        print("Recently_watched")
        episodes = {
            "showid": {
                "season_number": "1",
                "episode_number": "1"
            }
        }
        bus.emit('new:seen:episodes:{0}'.format(self.name), episodes)
