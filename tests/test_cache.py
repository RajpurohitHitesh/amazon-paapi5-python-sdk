import pytest
from amazon_paapi5.utils.cache import Cache

def test_cache_set_get():
    cache = Cache(ttl=10, maxsize=2)
    cache.set("key1", {"data": "value1"})
    assert cache.get("key1") == {"data": "value1"}
    cache.set("key2", {"data": "value2"})
    cache.set("key3", {"data": "value3"})  # Should evict key1
    assert cache.get("key1") is None