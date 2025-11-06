"""Unit tests for configuration"""

import pytest
from config.settings import Settings, LLMConfig, ChunkingConfig, get_test_settings


class TestSettings:
    """Test settings configuration"""

    def test_settings_creation(self):
        """Test creating settings"""
        settings = get_test_settings()
        assert settings.google_api_key == "test_key"
        assert settings.environment == "development"

    def test_llm_config(self):
        """Test LLM configuration"""
        config = LLMConfig()
        assert config.provider == "gemini"
        assert 0.0 <= config.temperature <= 2.0

    def test_chunking_config_validation(self):
        """Test chunking config validation"""
        with pytest.raises(ValueError):
            ChunkingConfig(chunk_size=100, chunk_overlap=150)

    def test_api_key_validation(self):
        """Test API key validation"""
        with pytest.raises(ValueError):
            Settings(google_api_key="your_google_api_key_here")
