"""Unit tests for caching"""

import pytest
from src.utils.cache import LRUCache, QueryCache
from config.settings import CacheConfig


class TestLRUCache:
    """Test LRU cache"""

    def test_cache_set_get(self):
        """Test basic set and get"""
        cache = LRUCache(max_size=10, ttl=3600)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_miss(self):
        """Test cache miss"""
        cache = LRUCache(max_size=10, ttl=3600)
        assert cache.get("nonexistent") is None

    def test_cache_eviction(self):
        """Test LRU eviction"""
        cache = LRUCache(max_size=2, ttl=3600)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = LRUCache(max_size=10, ttl=3600)
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5


class TestQueryCache:
    """Test query cache"""

    def test_query_cache_disabled(self):
        """Test cache when disabled"""
        config = CacheConfig(enabled=False)
        cache = QueryCache(config)

        cache.set("query1", "result1")
        assert cache.get("query1") is None

    def test_query_cache_enabled(self):
        """Test cache when enabled"""
        config = CacheConfig(enabled=True)
        cache = QueryCache(config)

        cache.set("query1", "result1")
        assert cache.get("query1") == "result1"
