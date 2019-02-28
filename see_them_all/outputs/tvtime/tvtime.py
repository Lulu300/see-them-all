from outputs import Output
from event_bus import EventBus
from util.constants import bus


class Tvtime(Output):

    def __init__(self, config):
        self.config = config

    def mark_as_watched(self, episode):
        print(episode)
        print("Mark as watched")
