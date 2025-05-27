import logging
from cachetools import TTLCache
from typing import Optional, Any, Union
import redis
import pickle
from datetime import datetime
import os
from pathlib import Path
from ..exceptions import CacheException

class Cache:
    """Enhanced caching system with file-based, Redis, and in-memory options."""
    
    def __init__(self, 
                 ttl: int = 3600, 
                 maxsize: int = 100, 
                 use_redis: bool = False,
                 use_file: bool = True,  # Default to file-based cache
                 base_path: str = "/root",  # Default root path
                 redis_url: str = "redis://localhost:6379",
                 namespace: str = "amazon_paapi5"):
        """
        Initialize cache with configurable backend.
        
        Args:
            ttl: Time-to-live in seconds for cached items (default: 1 hour)
            maxsize: Maximum number of items for in-memory cache
            use_redis: Whether to use Redis as cache backend
            use_file: Whether to use file-based cache
            base_path: Base directory for file cache
            redis_url: Redis connection URL
            namespace: Namespace for cache keys
        """
        self.ttl = ttl
        self.use_redis = use_redis
        self.use_file = use_file
        self.namespace = namespace
        self.logger = logging.getLogger(__name__)
        
        # Initialize statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0,
            'last_error': None,
            'last_error_time': None
        }
        
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
                return
            except Exception as e:
                self.logger.warning(f"File cache initialization failed: {e}. Falling back to memory cache.")
                self.use_file = False
        
        # Fall back to in-memory cache if neither Redis nor file cache is available
        if not (self.use_redis or self.use_file):
            self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
            self.logger.info(f"Using in-memory cache with maxsize={maxsize}")

    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path for given key."""
        safe_filename = "".join(c if c.isalnum() else "_" for c in key)
        return self.cache_dir / f"{safe_filename}.cache"

    def _update_error_stats(self, error: Exception) -> None:
        """Update error statistics."""
        self.stats['errors'] += 1
        self.stats['last_error'] = str(error)
        self.stats['last_error_time'] = datetime.utcnow().isoformat()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value or None if not found
            
        Raises:
            CacheException: If there's an error accessing the cache
        """
        try:
            if self.use_redis:
                data = self.redis_client.get(self._make_key(key))
                if data:
                    self.stats['hits'] += 1
                    return pickle.loads(data)
                self.stats['misses'] += 1
                return None
                
            elif self.use_file:
                cache_file = self._get_cache_path(key)
                if not cache_file.exists():
                    self.stats['misses'] += 1
                    return None
                    
                try:
                    with cache_file.open('rb') as f:
                        data = pickle.load(f)
                    
                    # Check expiration
                    if data['expires'] < datetime.utcnow().timestamp():
                        self.delete(key)
                        self.stats['misses'] += 1
                        return None
                    
                    self.stats['hits'] += 1
                    return data['value']
                except Exception:
                    self.delete(key)
                    self.stats['misses'] += 1
                    return None
                    
            else:
                value = self.cache.get(key)
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
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL in seconds
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            CacheException: If there's an error setting the cache
        """
        try:
            expiry = datetime.utcnow().timestamp() + (ttl if ttl is not None else self.ttl)
            
            if self.use_redis:
                return bool(self.redis_client.setex(
                    self._make_key(key),
                    ttl or self.ttl,
                    pickle.dumps(value)
                ))
                
            elif self.use_file:
                cache_file = self._get_cache_path(key)
                data = {
                    'key': key,
                    'value': value,
                    'expires': expiry,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                with cache_file.open('wb') as f:
                    pickle.dump(data, f)
                return True
                
            else:
                self.cache[key] = value
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
        try:
            if self.use_redis:
                return bool(self.redis_client.delete(self._make_key(key)))
                
            elif self.use_file:
                cache_file = self._get_cache_path(key)
                if cache_file.exists():
                    cache_file.unlink()
                return True
                
            else:
                if key in self.cache:
                    del self.cache[key]
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
                
            elif self.use_file:
                for cache_file in self.cache_dir.glob("*.cache"):
                    try:
                        cache_file.unlink()
                    except Exception:
                        continue
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
        
        if self.use_file:
            try:
                cache_files = list(self.cache_dir.glob("*.cache"))
                total_size = sum(f.stat().st_size for f in cache_files)
                stats.update({
                    'cache_dir': str(self.cache_dir),
                    'file_count': len(cache_files),
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2)
                })
            except Exception:
                pass
                
        return stats

    def _make_key(self, key: str) -> str:
        """Create namespaced key for Redis."""
        return f"{self.namespace}:{key}"

    def health_check(self) -> dict:
        """
        Check cache health status.
        
        Returns:
            dict: Health check results
        """
        status = {
            'healthy': True,
            'backend': 'redis' if self.use_redis else 'file' if self.use_file else 'memory',
            'stats': self.get_stats()
        }
        
        if self.use_redis:
            try:
                self.redis_client.ping()
            except redis.RedisError as e:
                status['healthy'] = False
                status['error'] = str(e)
        elif self.use_file:
            try:
                if not self.cache_dir.exists():
                    status['healthy'] = False
                    status['error'] = "Cache directory does not exist"
            except Exception as e:
                status['healthy'] = False
                status['error'] = str(e)
                
        return status