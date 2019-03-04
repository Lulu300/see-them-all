from inputs import Input
from urllib.parse import urljoin
from util.constants import PMS_WATCH_HISTORY, EB_NEW_SEEN_EP, bus
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


class Discord(Input):

    class VideoDescriptor(object):
        def __init__(self, j):
            self.__dict__ = json.loads(j)

    def __init__(self, name, config, cache_folder):
        self.name = name
        self.config = config
        self.cache_folder = cache_folder
        self.prefix = 'see-them-all[{0}]: '.format(self.config.get("uid"))

    def recently_watched(self):
        client = discord.Client()

        @client.event
        async def on_ready():
            channel = client.get_channel(id=int(self.config.get("channel")))
            list = await channel.history().flatten()
            videos = []
            for message in list:
                if len(message.content) > 6:
                    msg = message.content[3:len(message.content)-3]
                    if msg.startswith(self.prefix):
                        d = VideoSchema().load(json.loads(msg[len(self.prefix):])).data
                        if d.type_ == VideoType.EPISODE:
                            videos.append(Video(
                                d.title, VideoType.EPISODE,
                                Video.Id(tvdb_id=d.ids.tvdb_id, imdb_id=d.ids.imdb_id, tmdb_id=d.ids.tmdb_id),
                                d.season, d.episode
                            ))
                        elif d.type_ == VideoType.MOVIE:
                            videos.append(Video(
                                d.title, VideoType.MOVIE,
                                Video.Id(tvdb_id=d.ids.tvdb_id, imdb_id=d.ids.imdb_id, tmdb_id=d.ids.tmdb_id)
                            ))
            bus.emit('{0}:{1}'.format(EB_NEW_SEEN_EP, self.name), videos)
            await client.close()

        client.run(self.config.get("token"))
