"""Unit tests for the custom exception hierarchy."""

import pytest

from src.core.exceptions import (
    RAGException,
    ConfigurationError,
    APIKeyError,
    DocumentError,
    DocumentNotFoundError,
    DocumentLoadError,
    DocumentParseError,
    RAGIndexError,
    IndexCreationError,
    IndexLoadError,
    RetrievalError,
    QueryError,
    AgentError,
    AgentNotInitializedError,
    LLMError,
    LLMTimeoutError,
    LLMRateLimitError,
    InputValidationError,
    CacheError,
    SecurityError,
)


class TestRAGException:
    def test_basic_message(self):
        exc = RAGException("something broke")
        assert str(exc) == "something broke"
        assert exc.message == "something broke"

    def test_with_details(self):
        exc = RAGException("fail", details={"key": "value"})
        assert "key" in str(exc)
        assert exc.details == {"key": "value"}

    def test_with_original_error(self):
        original = ValueError("root cause")
        exc = RAGException("wrapper", original_error=original)
        assert "root cause" in str(exc)
        assert exc.original_error is original

    def test_empty_details_default(self):
        exc = RAGException("msg")
        assert exc.details == {}
        assert exc.original_error is None


class TestExceptionHierarchy:
    def test_config_errors(self):
        assert issubclass(ConfigurationError, RAGException)
        assert issubclass(APIKeyError, ConfigurationError)

    def test_document_errors(self):
        assert issubclass(DocumentError, RAGException)
        assert issubclass(DocumentNotFoundError, DocumentError)
        assert issubclass(DocumentLoadError, DocumentError)
        assert issubclass(DocumentParseError, DocumentError)

    def test_index_errors_no_shadow(self):
        # RAGIndexError must NOT shadow Python's built-in IndexError
        assert issubclass(RAGIndexError, RAGException)
        assert not issubclass(RAGIndexError, builtins_index_error())
        assert issubclass(IndexCreationError, RAGIndexError)
        assert issubclass(IndexLoadError, RAGIndexError)

    def test_retrieval_errors(self):
        assert issubclass(QueryError, RetrievalError)
        assert issubclass(RetrievalError, RAGException)

    def test_agent_errors(self):
        assert issubclass(AgentNotInitializedError, AgentError)
        assert issubclass(AgentError, RAGException)

    def test_llm_errors(self):
        assert issubclass(LLMTimeoutError, LLMError)
        assert issubclass(LLMRateLimitError, LLMError)

    def test_catch_rag_exception_catches_subtypes(self):
        with pytest.raises(RAGException):
            raise APIKeyError("bad key")

    def test_catch_document_error_catches_subtypes(self):
        with pytest.raises(DocumentError):
            raise DocumentNotFoundError("missing")


def builtins_index_error():
    """Return the built-in IndexError to avoid name confusion."""
    return IndexError
