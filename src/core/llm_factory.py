"""
LLM Factory - Multi-provider LLM initialization.

Supports Gemini (default), OpenAI, and Anthropic. Each non-default provider
is an optional dependency; a clear error message is raised if the required
package is not installed.
"""

from typing import Any

from src.utils.logging import get_logger
from config.settings import LLMConfig

logger = get_logger(__name__)


def create_llm(config: LLMConfig, api_key: str) -> Any:
    """Create an LLM instance based on the provider configuration.

    Args:
        config: LLM configuration with provider, model_name, temperature, etc.
        api_key: The API key for the chosen provider.

    Returns:
        A LlamaIndex-compatible LLM instance.

    Raises:
        ImportError: If the required provider package is not installed.
        ValueError: If the provider is not recognized.
    """
    provider = config.provider.lower()

    if provider == "gemini":
        return _create_gemini(config, api_key)
    elif provider == "openai":
        return _create_openai(config, api_key)
    elif provider == "anthropic":
        return _create_anthropic(config, api_key)
    else:
        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. "
            f"Supported providers: gemini, openai, anthropic"
        )


def _create_gemini(config: LLMConfig, api_key: str) -> Any:
    try:
        from llama_index.llms.gemini import Gemini
    except ImportError:
        raise ImportError(
            "Gemini provider requires 'llama-index-llms-gemini' and "
            "'google-generativeai'. Install with: "
            "pip install llama-index-llms-gemini google-generativeai"
        )

    llm = Gemini(
        model=config.model_name,
        api_key=api_key,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        timeout=config.timeout,
    )
    logger.info(f"Created Gemini LLM: {config.model_name}")
    return llm


def _create_openai(config: LLMConfig, api_key: str) -> Any:
    try:
        from llama_index.llms.openai import OpenAI
    except ImportError:
        raise ImportError(
            "OpenAI provider requires 'llama-index-llms-openai' and 'openai'. "
            "Install with: pip install llama-index-llms-openai openai"
        )

    model_name = config.model_name
    if model_name.startswith("models/"):
        model_name = "gpt-4o-mini"

    llm = OpenAI(
        model=model_name,
        api_key=api_key,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        timeout=float(config.timeout),
    )
    logger.info(f"Created OpenAI LLM: {model_name}")
    return llm


def _create_anthropic(config: LLMConfig, api_key: str) -> Any:
    try:
        from llama_index.llms.anthropic import Anthropic
    except ImportError:
        raise ImportError(
            "Anthropic provider requires 'llama-index-llms-anthropic' and "
            "'anthropic'. Install with: "
            "pip install llama-index-llms-anthropic anthropic"
        )

    model_name = config.model_name
    if model_name.startswith("models/"):
        model_name = "claude-3-haiku-20240307"

    llm = Anthropic(
        model=model_name,
        api_key=api_key,
        temperature=config.temperature,
        max_tokens=config.max_tokens or 4096,
        timeout=float(config.timeout),
    )
    logger.info(f"Created Anthropic LLM: {model_name}")
    return llm
