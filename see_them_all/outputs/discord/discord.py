from outputs import Output
from event_bus import EventBus
from util.constants import bus
from util.video import Video, VideoType
import discord
import asyncio
import json

class Discord(Output):

    def __init__(self, name, config, cache_folder):
        self.name = name
        self.config = config

    async def send_channel(self, channel, video):
        if video.type_ == VideoType.EPISODE:
            episode = {
                'type': 'episode',
                'title': video.title,
                'season': video.season_number,
                'episode': video.episode_number,
                'imdb_id': video.ids.imdb_id,
                'tvdb_id': video.ids.tvdb_id,
                'tmdb_id': video.ids.tmdb_id,
            }
            await channel.send('see-them-all[{0}]: {1}'.format(self.config.get("uid"), json.dumps(episode)))
        if video.type_ == VideoType.MOVIE:
            movie = {
                'type': 'movie',
                'title': video.title,
                'imdb_id': video.ids.imdb_id,
                'tvdb_id': video.ids.tvdb_id,
                'tmdb_id': video.ids.tmdb_id,
            }
            await channel.send('see-them-all[{0}]: {1}'.format(self.config.get("uid"), json.dumps(movie)))

    def mark_as_watched(self, videos):
        client = discord.Client()

        @client.event
        async def on_ready():
            channel = client.get_channel(id=int(self.config.get("channel")))
            for video in videos:
                await self.send_channel(channel, video)
            await client.close()

        client.run(self.config.get("token"))

    def write_cache_to_file(self):
        pass
