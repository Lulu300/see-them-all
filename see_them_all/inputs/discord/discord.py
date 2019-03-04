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
                if message.content.startswith(self.prefix):
                    d = VideoSchema.load(message.content[len(self.prefix):]).data
                    if d.type == 'episode':
                        videos.append(Video(
                            d.title, VideoType.EPISODE,
                            d.season, d.episode, tvdb_id=d.tvdb_id,
                            imdb_id=d.imdb_id, tmdb_id=d.tmdb_id,
                        ))
                    elif d.type == 'movies':
                        videos.append(Video(
                            d.title, VideoType.MOVIE, tvdb_id=d.tvdb_id,
                            imdb_id=d.imdb_id, tmdb_id=d.tmdb_id,
                        ))
            bus.emit('{0}:{1}'.format(EB_NEW_SEEN_EP, self.name), videos)
            await client.close()

        client.run(self.config.get("token"))
