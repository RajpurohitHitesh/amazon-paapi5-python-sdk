import logging
from cachetools import TTLCache
from typing import Optional, Any, Union
import redis
import pickle
from datetime import datetime
from ..exceptions import CacheException

class Cache:
    """Enhanced caching system with better error handling and monitoring."""
    
    def __init__(self, 
                 ttl: int = 3600, 
                 maxsize: int = 100, 
                 use_redis: bool = False, 
                 redis_url: str = "redis://localhost:6379",
                 namespace: str = "amazon_paapi5"):
        """
        Initialize cache with configurable backend.
        
        Args:
            ttl: Time-to-live in seconds for cached items
            maxsize: Maximum number of items for in-memory cache
            use_redis: Whether to use Redis as cache backend
            redis_url: Redis connection URL
            namespace: Namespace for cache keys
        """
        self.ttl = ttl
        self.use_redis = use_redis
        self.namespace = namespace
        self.logger = logging.getLogger(__name__)
        
        if use_redis:
            try:
                self.redis_client = redis.Redis.from_url(
                    redis_url,
                    socket_timeout=2,
                    retry_on_timeout=True,
                    decode_responses=False
                )
                # Test connection
                self.redis_client.ping()
                self.logger.info("Successfully connected to Redis")
            except redis.RedisError as e:
                self.logger.warning(f"Redis connection failed: {e}. Falling back to in-memory cache.")
                self.use_redis = False
                
        if not use_redis:
            self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
            self.logger.info(f"Using in-memory cache with maxsize={maxsize}")
            
        self.stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0,
            'last_error': None,
            'last_error_time': None
        }

    def _make_key(self, key: str) -> str:
        """Create namespaced cache key."""
        return f"{self.namespace}:{key}"

    def _update_error_stats(self, error: Exception) -> None:
        """Update error statistics."""
        self.stats['errors'] += 1
        self.stats['last_error'] = str(error)
        self.stats['last_error_time'] = datetime.utcnow().isoformat()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache with error handling and statistics.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value or None if not found
            
        Raises:
            CacheException: If there's an error accessing the cache
        """
        full_key = self._make_key(key)
        try:
            if self.use_redis:
                data = self.redis_client.get(full_key)
                if data:
                    self.stats['hits'] += 1
                    return pickle.loads(data)
                self.stats['misses'] += 1
                return None
            else:
                value = self.cache.get(full_key)
                if value is not None:
                    self.stats['hits'] += 1
                else:
                    self.stats['misses'] += 1
                return value
        except Exception as e:
            self._update_error_stats(e)
            self.logger.error(f"Cache get error: {str(e)}", exc_info=True)
            raise CacheException(f"Failed to get cache key: {key}", cache_operation="get")

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with custom TTL option.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL in seconds
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            CacheException: If there's an error setting the cache
        """
        full_key = self._make_key(key)
        try:
            if self.use_redis:
                expiry = ttl or self.ttl
                success = bool(self.redis_client.setex(
                    full_key,
                    expiry,
                    pickle.dumps(value)
                ))
                if not success:
                    raise CacheException("Redis set operation failed", cache_operation="set")
                return success
            else:
                self.cache[full_key] = value
                return True
        except Exception as e:
            self._update_error_stats(e)
            self.logger.error(f"Cache set error: {str(e)}", exc_info=True)
            raise CacheException(f"Failed to set cache key: {key}", cache_operation="set")

    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            CacheException: If there's an error deleting from cache
        """
        full_key = self._make_key(key)
        try:
            if self.use_redis:
                return bool(self.redis_client.delete(full_key))
            else:
                if full_key in self.cache:
                    del self.cache[full_key]
                    return True
                return False
        except Exception as e:
            self._update_error_stats(e)
            self.logger.error(f"Cache delete error: {str(e)}", exc_info=True)
            raise CacheException(f"Failed to delete cache key: {key}", cache_operation="delete")

    def clear(self) -> bool:
        """
        Clear all cached data.
        
        Returns:
            bool: True if successful
            
        Raises:
            CacheException: If there's an error clearing the cache
        """
        try:
            if self.use_redis:
                pattern = f"{self.namespace}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    return bool(self.redis_client.delete(*keys))
                return True
            else:
                self.cache.clear()
                return True
        except Exception as e:
            self._update_error_stats(e)
            self.logger.error(f"Cache clear error: {str(e)}", exc_info=True)
            raise CacheException("Failed to clear cache", cache_operation="clear")

    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            dict: Cache statistics including hits, misses, errors, and hit ratio
        """
        stats = self.stats.copy()
        total_requests = stats['hits'] + stats['misses']
        stats['hit_ratio'] = (
            stats['hits'] / total_requests
            if total_requests > 0
            else 0
        )
        stats['total_requests'] = total_requests
        return stats

    def health_check(self) -> dict:
        """
        Check cache health status.
        
        Returns:
            dict: Health check results
        """
        status = {
            'healthy': True,
            'backend': 'redis' if self.use_redis else 'memory',
            'stats': self.get_stats()
        }
        
        if self.use_redis:
            try:
                self.redis_client.ping()
            except redis.RedisError as e:
                status['healthy'] = False
                status['error'] = str(e)
        
        return status