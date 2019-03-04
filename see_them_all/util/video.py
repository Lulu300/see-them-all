from enum import Enum
from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField


class VideoType(str, Enum):
    EPISODE = 'episode'
    MOVIE = 'movie'


class IdSchema(Schema):
    tvdb_id = fields.Int(required=False, allow_none=True, default=None, missing=None)
    tmdb_id = fields.Int(required=False, allow_none=True, default=None, missing=None)
    imdb_id = fields.Int(required=False, allow_none=True, default=None, missing=None)

    @post_load
    def make_Id(self, data):
        return Video.Id(**data)


class VideoSchema(Schema):
    title = fields.String()
    type_ = EnumField(VideoType)
    season_number = fields.Int(required=False, allow_none=True, default=None, missing=None)
    episode_number = fields.Int(required=False, allow_none=True, default=None, missing=None)
    watched_at = fields.Int(required=False, allow_none=True, default=None, missing=None)
    ids = fields.Nested(IdSchema)

    @post_load
    def make_video(self, data):
        return Video(**data)


class Video(object):

    def __init__(self, title: str, type_: VideoType, ids, season_number=None, episode_number=None, watched_at=None):
        self.type_ = type_
        self.title = title
        self.season_number = season_number
        self.episode_number = episode_number
        self.watched_at = watched_at
        self.ids = ids

    def __str__(self):
        return 'title: {0.title}, type_: {0.type_.value}, season_number: {0.season_number}, episode_number: {0.episode_number}, watched_at: {0.watched_at}, ids: [{0.ids}]'.format(self)

    def __str__(self):
        return 'title: {0.title}, type_: {0.type_.value}, season_number: {0.season_number}, episode_number: {0.episode_number}, watched_at: {0.watched_at}, ids: [{0.ids}]'.format(self)

    class Id(object):

        def __init__(self, tvdb_id=None, tmdb_id=None, imdb_id=None):
            self.tvdb_id = tvdb_id
            self.tmdb_id = tmdb_id
            self.imdb_id = imdb_id

        def __str__(self):
            return 'tvdb_id: {0.tvdb_id}, tmdb_id: {0.tmdb_id}, imdb_id: {0.imdb_id}'.format(self)

        def __str__(self):
            return 'tvdb_id: {0.tvdb_id}, tmdb_id: {0.tmdb_id}, imdb_id: {0.imdb_id}'.format(self)
