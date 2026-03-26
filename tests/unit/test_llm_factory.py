"""Unit tests for the LLM factory."""

import pytest
from unittest.mock import patch, MagicMock

from config.settings import LLMConfig
from src.core.llm_factory import create_llm


class TestCreateLLM:
    def test_unsupported_provider_raises(self):
        config = LLMConfig(provider="gemini")
        # Override to something invalid
        object.__setattr__(config, "provider", "unknown_provider")
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_llm(config, "fake_key")

    def test_gemini_import_error(self):
        config = LLMConfig(provider="gemini")
        with patch.dict("sys.modules", {"llama_index.llms.gemini": None}):
            with pytest.raises(ImportError, match="llama-index-llms-gemini"):
                create_llm(config, "fake_key")

    def test_openai_import_error(self):
        config = LLMConfig(provider="openai")
        with patch.dict("sys.modules", {"llama_index.llms.openai": None}):
            with pytest.raises(ImportError, match="llama-index-llms-openai"):
                create_llm(config, "fake_key")

    def test_anthropic_import_error(self):
        config = LLMConfig(provider="anthropic")
        with patch.dict("sys.modules", {"llama_index.llms.anthropic": None}):
            with pytest.raises(ImportError, match="llama-index-llms-anthropic"):
                create_llm(config, "fake_key")
