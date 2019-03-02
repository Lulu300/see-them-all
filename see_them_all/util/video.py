from enum import Enum


class VideoType(Enum):
    EPISODE = 'episode'
    MOVIE = 'movie'


class Video(object):

    def __init__(self, title, type_: VideoType, season_number=None, episode_number=None, tvdb_id=None, tmdb_id=None, imdb_id=None):
        if type(type_) is not VideoType:
            raise TypeError('type_ must be typed as : VideoType')
        self.title = title
        self.type_ = type_
        self.season_number = season_number
        self.episode_number = episode_number
        self.ids = Video.Id(tvdb_id, tmdb_id, imdb_id)

    def __repr__(self):
        return 'title: {0}, type_: {1}, season_number: {2}, episode_number: {3}, ids: [{4}]'.format(self.title, self.type_, self.season_number, self.episode_number, self.ids)

    def __str__(self):
        return 'title: {0}, type_: {1}, season_number: {2}, episode_number: {3}, ids: [{4}]'.format(self.title, self.type_, self.season_number, self.episode_number, self.ids)

    class Id(object):

        def __init__(self, tvdb_id=None, tmdb_id=None, imdb_id=None):
            self.tvdb_id = tvdb_id
            self.tmdb_id = tmdb_id
            self.imdb_id = imdb_id

        def __repr__(self):
            return 'tvdb_id: {0}, tmdb_id: {1}, imdb_id: {2}'.format(self.tvdb_id, self.tmdb_id, self.imdb_id)

        def __str__(self):
            return 'tvdb_id: {0}, tmdb_id: {1}, imdb_id: {2}'.format(self.tvdb_id, self.tmdb_id, self.imdb_id)
