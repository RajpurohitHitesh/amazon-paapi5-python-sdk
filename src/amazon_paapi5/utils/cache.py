from cachetools import TTLCache
from typing import Optional, Any
import redis
import pickle

class Cache:
    def __init__(self, ttl: int = 3600, maxsize: int = 100, use_redis: bool = False, redis_url: str = "redis://localhost:6379"):
        self.ttl = ttl
        self.use_redis = use_redis
        if use_redis:
            try:
                self.redis_client = redis.Redis.from_url(redis_url)
            except redis.RedisError as e:
                print(f"Redis connection failed: {e}. Falling back to in-memory cache.")
                self.use_redis = False
        if not use_redis:
            self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str) -> Optional[Any]:
        if self.use_redis:
            try:
                data = self.redis_client.get(key)
                if data:
                    return pickle.loads(data)
                return None
            except redis.RedisError:
                return None
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        if self.use_redis:
            try:
                self.redis_client.setex(key, self.ttl, pickle.dumps(value))
            except redis.RedisError:
                pass
        else:
            self.cache[key] = value