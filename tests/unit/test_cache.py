"""Unit tests for caching."""

import time
import threading
import pytest
from src.utils.cache import LRUCache, QueryCache
from config.settings import CacheConfig


class TestLRUCache:
    def test_cache_set_get(self):
        cache = LRUCache(max_size=10, ttl=3600)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_miss(self):
        cache = LRUCache(max_size=10, ttl=3600)
        assert cache.get("nonexistent") is None

    def test_cache_eviction(self):
        cache = LRUCache(max_size=2, ttl=3600)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_stats(self):
        cache = LRUCache(max_size=10, ttl=3600)
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_cache_overwrite(self):
        cache = LRUCache(max_size=10, ttl=3600)
        cache.set("key1", "old")
        cache.set("key1", "new")
        assert cache.get("key1") == "new"
        assert len(cache) == 1

    def test_cache_delete(self):
        cache = LRUCache(max_size=10, ttl=3600)
        cache.set("key1", "value1")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.delete("key1") is False

    def test_cache_clear(self):
        cache = LRUCache(max_size=10, ttl=3600)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert len(cache) == 0
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_cache_contains(self):
        cache = LRUCache(max_size=10, ttl=3600)
        cache.set("key1", "value1")
        assert "key1" in cache
        assert "key2" not in cache

    def test_expired_entry_returns_none(self):
        cache = LRUCache(max_size=10, ttl=0)  # 0 second TTL
        cache.set("key1", "value1")
        time.sleep(0.01)
        assert cache.get("key1") is None

    def test_lru_order(self):
        """Access key1 so key2 becomes least recently used."""
        cache = LRUCache(max_size=2, ttl=3600)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # makes key1 most recent
        cache.set("key3", "value3")  # should evict key2

        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"

    def test_access_count_increments(self):
        cache = LRUCache(max_size=10, ttl=3600)
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key1")
        # Internal state check via the entry
        entry = cache._cache["key1"]
        assert entry.access_count == 2

    def test_thread_safety(self):
        cache = LRUCache(max_size=1000, ttl=3600)
        errors = []

        def writer(start):
            try:
                for i in range(100):
                    cache.set(f"key_{start}_{i}", f"val_{i}")
            except Exception as e:
                errors.append(e)

        def reader(start):
            try:
                for i in range(100):
                    cache.get(f"key_{start}_{i}")
            except Exception as e:
                errors.append(e)

        threads = []
        for t in range(5):
            threads.append(threading.Thread(target=writer, args=(t,)))
            threads.append(threading.Thread(target=reader, args=(t,)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestQueryCache:
    def test_query_cache_disabled(self):
        config = CacheConfig(enabled=False)
        cache = QueryCache(config)
        cache.set("query1", "result1")
        assert cache.get("query1") is None

    def test_query_cache_enabled(self):
        config = CacheConfig(enabled=True)
        cache = QueryCache(config)
        cache.set("query1", "result1")
        assert cache.get("query1") == "result1"

    def test_query_cache_clear(self):
        config = CacheConfig(enabled=True)
        cache = QueryCache(config)
        cache.set("query1", "result1")
        cache.clear()
        assert cache.get("query1") is None

    def test_query_cache_stats_enabled(self):
        config = CacheConfig(enabled=True)
        cache = QueryCache(config)
        stats = cache.get_stats()
        assert "size" in stats

    def test_query_cache_stats_disabled(self):
        config = CacheConfig(enabled=False)
        cache = QueryCache(config)
        stats = cache.get_stats()
        assert stats == {"enabled": False}

    def test_different_queries_different_keys(self):
        config = CacheConfig(enabled=True)
        cache = QueryCache(config)
        cache.set("query1", "result1")
        cache.set("query2", "result2")
        assert cache.get("query1") == "result1"
        assert cache.get("query2") == "result2"
