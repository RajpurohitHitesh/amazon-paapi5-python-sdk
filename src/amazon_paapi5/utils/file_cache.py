import os
import json
import pickle
import time
from typing import Optional, Any
from pathlib import Path
from datetime import datetime

class FileCache:
    """File-based cache implementation similar to PHP SDK."""
    
    def __init__(self, 
                 base_path: str = None,
                 ttl: int = 3600):
        """
        Initialize file cache.
        
        Args:
            base_path: Base directory path (default: current working directory)
            ttl: Time-to-live in seconds
        """
        if base_path:
            self.base_dir = Path(base_path)
        else:
            # Get the root directory (where the script is running)
            self.base_dir = Path(os.getcwd())

        # Construct cache directory path: root/storage/cache/amazon
        self.cache_dir = self.base_dir / "storage" / "cache" / "amazon"
        self.ttl = ttl
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            # Create a .gitignore file to exclude cache files from git
            gitignore_file = self.cache_dir / '.gitignore'
            if not gitignore_file.exists():
                with gitignore_file.open('w') as f:
                    f.write('*\n!.gitignore\n')
        except Exception as e:
            raise RuntimeError(f"Failed to create cache directory: {str(e)}")
        
    def _get_cache_path(self, key: str) -> Path:
        """
        Get full path for cache file.
        
        Args:
            key: Cache key to generate filename
            
        Returns:
            Path object for the cache file
        """
        # Generate a safe filename from the key
        safe_filename = "".join(c if c.isalnum() else "_" for c in key)
        return self.cache_dir / f"{safe_filename}.cache"
        
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache file.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_file = self._get_cache_path(key)
        
        if not cache_file.exists():
            return None
            
        try:
            with cache_file.open('rb') as f:
                data = pickle.load(f)
                
            # Check if cache has expired
            if time.time() > data['expires']:
                self.delete(key)
                return None
                
            return data['value']
        except Exception:
            # If there's any error reading the cache, clean it up
            self.delete(key)
            return None
            
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Save value to cache file.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        cache_file = self._get_cache_path(key)
        expiry = time.time() + (ttl if ttl is not None else self.ttl)
        
        try:
            data = {
                'key': key,
                'value': value,
                'expires': expiry,
                'created_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with cache_file.open('wb') as f:
                pickle.dump(data, f)
            return True
        except Exception:
            return False
            
    def delete(self, key: str) -> bool:
        """
        Delete cache file.
        
        Args:
            key: Cache key to delete
            
        Returns:
            bool: True if deleted or didn't exist, False on error
        """
        cache_file = self._get_cache_path(key)
        try:
            if cache_file.exists():
                cache_file.unlink()
            return True
        except Exception:
            return False
            
    def clear(self) -> bool:
        """
        Delete all cache files.
        
        Returns:
            bool: True if successful, False on error
        """
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                except Exception:
                    continue
            return True
        except Exception:
            return False

    def get_cache_info(self) -> dict:
        """
        Get information about the cache directory.
        
        Returns:
            dict: Information about cache directory and files
        """
        try:
            cache_files = list(self.cache_dir.glob("*.cache"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'cache_dir': str(self.cache_dir),
                'file_count': len(cache_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except Exception:
            return {
                'cache_dir': str(self.cache_dir),
                'error': 'Failed to get cache information'
            }