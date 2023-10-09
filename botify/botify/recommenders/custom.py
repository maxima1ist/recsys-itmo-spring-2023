from .indexed import Indexed
from .contextual import Contextual
from .recommender import Recommender
import random


class Custom(Recommender):
    TOP = 20

    def __init__(self, tracks_redis, recommendations_redis, catalog):
        self.tracks_redis = tracks_redis
        self.catalog = catalog
        self.indexed_fallback = Indexed(tracks_redis, recommendations_redis, catalog.top_tracks[:Custom.TOP], catalog)
        self.contextual_fallback = Contextual(tracks_redis, catalog)
        
    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if prev_track_time < 0.7:
            return self.indexed_fallback.recommend_next(user, prev_track, prev_track_time)
        
        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.indexed_fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if recommendations is None:
            return self.indexed_fallback.recommend_next(user, prev_track, prev_track_time)

        shuffled = list(recommendations)[:Custom.TOP]
        random.shuffle(shuffled)
        return shuffled[0]
