"""Shared test fixtures for the RAG test suite."""

import pytest
from config.settings import get_test_settings, CacheConfig


@pytest.fixture
def test_settings():
    """Return a Settings instance configured for testing."""
    return get_test_settings()


@pytest.fixture
def cache_config_enabled():
    """Return an enabled CacheConfig."""
    return CacheConfig(enabled=True, max_size=100, ttl=60)


@pytest.fixture
def cache_config_disabled():
    """Return a disabled CacheConfig."""
    return CacheConfig(enabled=False)
