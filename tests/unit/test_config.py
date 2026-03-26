"""Unit tests for configuration."""

import pytest
from config.settings import (
    Settings,
    LLMConfig,
    EmbeddingConfig,
    ChunkingConfig,
    CacheConfig,
    VectorStoreConfig,
    get_test_settings,
)


class TestSettings:
    def test_settings_creation(self):
        settings = get_test_settings()
        assert settings.google_api_key == "test_key"
        assert settings.environment == "development"

    def test_placeholder_api_key_rejected(self):
        with pytest.raises(ValueError):
            Settings(google_api_key="your_google_api_key_here")

    def test_empty_api_key_rejected(self):
        with pytest.raises(ValueError):
            Settings(google_api_key="")

    def test_test_settings_overrides(self):
        settings = get_test_settings(google_api_key="custom_key")
        assert settings.google_api_key == "custom_key"

    def test_debug_enabled_in_test(self):
        settings = get_test_settings()
        assert settings.debug is True


class TestLLMConfig:
    def test_defaults(self):
        config = LLMConfig()
        assert config.provider == "gemini"
        assert config.temperature == 0.1
        assert config.max_retries == 3

    def test_temperature_bounds(self):
        assert LLMConfig(temperature=0.0).temperature == 0.0
        assert LLMConfig(temperature=2.0).temperature == 2.0

    def test_temperature_out_of_bounds(self):
        with pytest.raises(ValueError):
            LLMConfig(temperature=3.0)
        with pytest.raises(ValueError):
            LLMConfig(temperature=-0.1)

    def test_valid_providers(self):
        for provider in ("gemini", "openai", "anthropic"):
            config = LLMConfig(provider=provider)
            assert config.provider == provider


class TestEmbeddingConfig:
    def test_defaults(self):
        config = EmbeddingConfig()
        assert config.provider == "huggingface"
        assert config.model_name == "BAAI/bge-small-en-v1.5"


class TestChunkingConfig:
    def test_defaults(self):
        config = ChunkingConfig()
        assert config.chunk_size == 1024
        assert config.chunk_overlap == 200

    def test_overlap_must_be_less_than_size(self):
        with pytest.raises(ValueError):
            ChunkingConfig(chunk_size=100, chunk_overlap=150)

    def test_overlap_equals_size_rejected(self):
        with pytest.raises(ValueError):
            ChunkingConfig(chunk_size=100, chunk_overlap=100)

    def test_valid_custom_values(self):
        config = ChunkingConfig(chunk_size=512, chunk_overlap=50)
        assert config.chunk_size == 512
        assert config.chunk_overlap == 50


class TestCacheConfig:
    def test_defaults(self):
        config = CacheConfig()
        assert config.enabled is True
        assert config.ttl == 3600
        assert config.max_size == 1000

    def test_disabled(self):
        config = CacheConfig(enabled=False)
        assert config.enabled is False


class TestVectorStoreConfig:
    def test_defaults(self):
        config = VectorStoreConfig()
        assert config.type == "chroma"

    def test_valid_types(self):
        for t in ("chroma", "faiss", "memory"):
            config = VectorStoreConfig(type=t)
            assert config.type == t
