import logging
from cachetools import TTLCache
from typing import Optional, Any, Union
import redis
import pickle
from datetime import datetime
import os
from pathlib import Path
from ..exceptions import CacheException
import collections

class Cache:
    """Enhanced caching system with file-based, Redis, and in-memory options."""
    
    def __init__(self, 
                 ttl: int = 3600, 
                 maxsize: int = 100, 
                 use_redis: bool = False,
                 use_file: bool = True,
                 base_path: str = None,
                 redis_url: str = "redis://localhost:6379",
                 namespace: str = "amazon_paapi5"):
        """
        Initialize cache with configurable backend.
        
        Args:
            ttl: Time-to-live in seconds for cached items (default: 1 hour)
            maxsize: Maximum number of items for in-memory cache
            use_redis: Whether to use Redis as cache backend
            use_file: Whether to use file-based cache
            base_path: Base directory for file cache (default: user's home directory)
            redis_url: Redis connection URL
            namespace: Namespace for cache keys
        """
        self.ttl = ttl
        self.maxsize = maxsize
        self.use_redis = use_redis
        self.use_file = use_file
        self.namespace = namespace
        self.logger = logging.getLogger(__name__)
        
        # Use user's home directory if base_path is None
        if base_path is None:
            from pathlib import Path
            base_path = str(Path.home())
        
        # Initialize statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0,
            'last_error': None,
            'last_error_time': None
        }
        
        # Initialize key tracker for all cache types
        self.key_tracker = collections.OrderedDict()
        
        # Try Redis if specified
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
                self.logger.info("Successfully connected to Redis cache")
            except redis.RedisError as e:
                self.logger.warning(f"Redis connection failed: {e}. Falling back to file cache.")
                self.use_redis = False
        
        # Try file-based cache if Redis is not used
        if use_file and not self.use_redis:
            try:
                self.cache_dir = Path(base_path) / "storage" / "cache" / "amazon"
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                
                # Create .gitignore file
                gitignore_path = self.cache_dir / '.gitignore'
                if not gitignore_path.exists():
                    with gitignore_path.open('w') as f:
                        f.write('*\n!.gitignore\n')
                        
                self.logger.info(f"Using file-based cache in {self.cache_dir}")
            except Exception as e:
                self.logger.warning(f"File cache initialization failed: {e}. Falling back to memory cache.")
                self.use_file = False
        
        # Fall back to in-memory cache if neither Redis nor file cache is available
        if not (self.use_redis or self.use_file):
            self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
            self.logger.info(f"Using in-memory cache with maxsize={maxsize}")
    
    def _enforce_maxsize(self, new_key=None):
        """Enforce maxsize by removing oldest items if needed."""
        if new_key is not None:
            self.key_tracker[new_key] = datetime.now().timestamp()
            
        # If we've exceeded maxsize, remove oldest item(s)
        while len(self.key_tracker) > self.maxsize:
            oldest_key = next(iter(self.key_tracker))
            self.delete(oldest_key.split(':', 1)[1])  # Remove namespace prefix
            self.key_tracker.pop(oldest_key)

    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path for given key."""
        safe_filename = "".join(c if c.isalnum() else "_" for c in key)
        return self.cache_dir / f"{safe_filename}.cache"

    def _update_error_stats(self, error: Exception) -> None:
        """Update error statistics."""
        self.stats['errors'] += 1
        self.stats['last_error'] = str(error)
        self.stats['last_error_time'] = datetime.utcnow().isoformat()

    def get(self, key: str) -> Any:
        """Get value from cache."""
        full_key = f"{self.namespace}:{key}"
        
        try:
            if self.use_redis:
                data = self.redis_client.get(full_key)
                if data:
                    self.key_tracker[full_key] = datetime.now().timestamp()
                    self.stats['hits'] += 1
                    return pickle.loads(data)
                self.stats['misses'] += 1
                return None
            
            elif self.use_file:
                cache_path = self._get_cache_path(full_key)
                
                if not cache_path.exists():
                    self.stats['misses'] += 1
                    return None
                
                # Check if file is expired
                modified_time = cache_path.stat().st_mtime
                if (datetime.now().timestamp() - modified_time) > self.ttl:
                    self.stats['misses'] += 1
                    cache_path.unlink(missing_ok=True)
                    if full_key in self.key_tracker:
                        self.key_tracker.pop(full_key)
                    return None
                
                with cache_path.open('rb') as f:
                    data = pickle.load(f)
                    self.key_tracker[full_key] = datetime.now().timestamp()
                    self.stats['hits'] += 1
                    return data
            
            else:  # In-memory cache
                if full_key in self.cache:
                    self.stats['hits'] += 1
                    return self.cache[full_key]
                self.stats['misses'] += 1
                return None
                
        except Exception as e:
            self._update_error_stats(e)
            self.logger.error(f"Cache get error: {str(e)}")
            return None

    def set(self, key: str, value: Any) -> bool:
        """Set value in cache."""
        full_key = f"{self.namespace}:{key}"
        
        try:
            if self.use_redis:
                serialized = pickle.dumps(value)
                result = bool(self.redis_client.setex(full_key, self.ttl, serialized))
                self._enforce_maxsize(full_key)
                return result
            
            elif self.use_file:
                self._enforce_maxsize(full_key)
                cache_path = self._get_cache_path(full_key)
                
                with cache_path.open('wb') as f:
                    pickle.dump(value, f)
                    
                return True
            
            else:  # In-memory cache
                self.cache[full_key] = value
                return True
                
        except Exception as e:
            self._update_error_stats(e)
            self.logger.error(f"Cache set error: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        full_key = f"{self.namespace}:{key}"
        
        try:
            if full_key in self.key_tracker:
                self.key_tracker.pop(full_key)
                
            if self.use_redis:
                return bool(self.redis_client.delete(full_key))
            
            elif self.use_file:
                cache_path = self._get_cache_path(full_key)
                if cache_path.exists():
                    cache_path.unlink()
                return True
            
            else:  # In-memory cache
                if full_key in self.cache:
                    del self.cache[full_key]
                return True
                
        except Exception as e:
            self._update_error_stats(e)
            self.logger.error(f"Cache delete error: {str(e)}")
            return False

    def clear(self) -> bool:
        """Clear all cached values."""
        try:
            self.key_tracker.clear()
            
            if self.use_redis:
                keys = self.redis_client.keys(f"{self.namespace}:*")
                if keys:
                    return bool(self.redis_client.delete(*keys))
                return True
            
            elif self.use_file:
                for path in self.cache_dir.glob("*.cache"):
                    path.unlink(missing_ok=True)
                return True
            
            else:  # In-memory cache
                self.cache.clear()
                return True
                
        except Exception as e:
            self._update_error_stats(e)
            self.logger.error(f"Cache clear error: {str(e)}")
            return False

    def get_stats(self) -> dict:
        """Get cache statistics."""
        stats = dict(self.stats)
        
        # Calculate hit ratio
        total = stats['hits'] + stats['misses']
        stats['hit_ratio'] = stats['hits'] / total if total > 0 else 0
        
        # Add cache type
        if self.use_redis:
            stats['type'] = 'redis'
        elif self.use_file:
            stats['type'] = 'file'
            stats['location'] = str(self.cache_dir)
        else:
            stats['type'] = 'memory'
            stats['size'] = len(self.cache) if hasattr(self, 'cache') else 0
            stats['maxsize'] = self.cache.maxsize if hasattr(self, 'cache') else 0
            
        return stats
    
    def get_many(self, keys: list) -> dict:
        """Get multiple values from cache."""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def set_many(self, items: dict) -> bool:
        """Set multiple values in cache."""
        success = True
        for key, value in items.items():
            if not self.set(key, value):
                success = False
        return success
    
    def delete_many(self, keys: list) -> bool:
        """Delete multiple values from cache."""
        success = True
        for key in keys:
            if not self.delete(key):
                success = False
        return success
    
    def get_or_set(self, key: str, value_func: callable, ttl: Optional[int] = None) -> Any:
        """Get value from cache or compute and store it."""
        value = self.get(key)
        if value is None:
            value = value_func()
            self.set(key, value)
        return value
    
    def touch(self, key: str) -> bool:
        """Update TTL for key."""
        value = self.get(key)
        if value is not None:
            return self.set(key, value)
        return False
    
    def contains(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self.get(key) is not None
    
    def incr(self, key: str, delta: int = 1) -> int:
        """Increment value in cache."""
        value = self.get(key) or 0
        value += delta
        self.set(key, value)
        return value
    
    def decr(self, key: str, delta: int = 1) -> int:
        """Decrement value in cache."""
        return self.incr(key, -delta)
    
    def close(self) -> None:
        """Close cache connections."""
        if self.use_redis and hasattr(self, 'redis_client'):
            self.redis_client.close()