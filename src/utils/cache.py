"""
Caching Layer for RAG System
LRU cache with TTL support
"""

from typing import Any, Optional, Dict, Callable
from collections import OrderedDict
from datetime import datetime, timedelta
import hashlib
import json
import functools

from src.models.schemas import CacheEntry
from src.utils.logging import get_logger
from config.settings import CacheConfig

logger = get_logger(__name__)


class LRUCache:
    """LRU (Least Recently Used) Cache with TTL support"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Initialize LRU cache

        Args:
            max_size: Maximum number of items
            ttl: Time to live in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0

        logger.info(
            "LRU cache initialized",
            extra={"max_size": max_size, "ttl": ttl}
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]

        # Check if expired
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            logger.debug(f"Cache expired: {key}")
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)

        # Update access info
        entry.accessed_at = datetime.utcnow()
        entry.access_count += 1

        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
        """
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            ttl=self.ttl
        )

        # Remove if already exists
        if key in self._cache:
            del self._cache[key]

        # Add to cache
        self._cache[key] = entry

        # Evict least recently used if over max size
        if len(self._cache) > self.max_size:
            evicted_key, _ = self._cache.popitem(last=False)
            logger.debug(f"Cache eviction: {evicted_key}")

    def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary of cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        return key in self._cache


class QueryCache:
    """Specialized cache for query results"""

    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize query cache

        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()

        if self.config.enabled:
            self.cache = LRUCache(
                max_size=self.config.max_size,
                ttl=self.config.ttl
            )
        else:
            self.cache = None

        logger.info(
            "Query cache initialized",
            extra={"enabled": self.config.enabled}
        )

    def _generate_key(self, query: str, **kwargs) -> str:
        """
        Generate cache key from query and parameters

        Args:
            query: Query string
            **kwargs: Additional parameters

        Returns:
            Cache key (hash)
        """
        # Create deterministic string from query and params
        key_data = {
            "query": query,
            **kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)

        # Hash for fixed-length key
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, query: str, **kwargs) -> Optional[Any]:
        """
        Get cached query result

        Args:
            query: Query string
            **kwargs: Additional parameters

        Returns:
            Cached result or None
        """
        if not self.config.enabled or self.cache is None:
            return None

        key = self._generate_key(query, **kwargs)
        result = self.cache.get(key)

        if result is not None:
            logger.debug(f"Cache hit for query: {query[:50]}...")
        else:
            logger.debug(f"Cache miss for query: {query[:50]}...")

        return result

    def set(self, query: str, result: Any, **kwargs) -> None:
        """
        Cache query result

        Args:
            query: Query string
            result: Query result
            **kwargs: Additional parameters
        """
        if not self.config.enabled or self.cache is None:
            return

        key = self._generate_key(query, **kwargs)
        self.cache.set(key, result)
        logger.debug(f"Cached result for query: {query[:50]}...")

    def clear(self) -> None:
        """Clear cache"""
        if self.cache:
            self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.cache:
            return self.cache.get_stats()
        return {
            "enabled": False
        }


def cached(cache_instance: QueryCache, **cache_kwargs):
    """
    Decorator to cache function results

    Args:
        cache_instance: QueryCache instance
        **cache_kwargs: Additional cache parameters

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from args
            if args:
                query_arg = args[0] if len(args) > 0 else ""
            else:
                query_arg = kwargs.get('query', '')

            # Check cache
            cached_result = cache_instance.get(str(query_arg), **cache_kwargs)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache_instance.set(str(query_arg), result, **cache_kwargs)

            return result
        return wrapper
    return decorator
