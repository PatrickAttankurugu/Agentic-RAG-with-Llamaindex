"""
Custom Exception Hierarchy
Industry-standard error handling for RAG applications
"""

from typing import Optional, Dict, Any


class RAGException(Exception):
    """Base exception for all RAG-related errors"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.details = details or {}
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        base_msg = self.message
        if self.details:
            base_msg += f" | Details: {self.details}"
        if self.original_error:
            base_msg += f" | Caused by: {str(self.original_error)}"
        return base_msg


# Configuration Errors
class ConfigurationError(RAGException):
    """Raised when configuration is invalid or missing"""
    pass


class APIKeyError(ConfigurationError):
    """Raised when API key is missing or invalid"""
    pass


# Document Processing Errors
class DocumentError(RAGException):
    """Base exception for document-related errors"""
    pass


class DocumentNotFoundError(DocumentError):
    """Raised when a document cannot be found"""
    pass


class DocumentLoadError(DocumentError):
    """Raised when a document fails to load"""
    pass


class DocumentParseError(DocumentError):
    """Raised when a document cannot be parsed"""
    pass


# Index Errors
class IndexError(RAGException):
    """Base exception for index-related errors"""
    pass


class IndexCreationError(IndexError):
    """Raised when index creation fails"""
    pass


class IndexLoadError(IndexError):
    """Raised when index loading fails"""
    pass


class IndexPersistError(IndexError):
    """Raised when index persistence fails"""
    pass


# Retrieval Errors
class RetrievalError(RAGException):
    """Base exception for retrieval errors"""
    pass


class QueryError(RetrievalError):
    """Raised when a query fails"""
    pass


class EmbeddingError(RetrievalError):
    """Raised when embedding generation fails"""
    pass


# Agent Errors
class AgentError(RAGException):
    """Base exception for agent-related errors"""
    pass


class AgentNotInitializedError(AgentError):
    """Raised when agent is used before initialization"""
    pass


class AgentExecutionError(AgentError):
    """Raised when agent execution fails"""
    pass


class ToolExecutionError(AgentError):
    """Raised when a tool execution fails"""
    pass


# LLM Errors
class LLMError(RAGException):
    """Base exception for LLM-related errors"""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out"""
    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limit is exceeded"""
    pass


class LLMResponseError(LLMError):
    """Raised when LLM response is invalid"""
    pass


# Validation Errors
class ValidationError(RAGException):
    """Base exception for validation errors"""
    pass


class InputValidationError(ValidationError):
    """Raised when input validation fails"""
    pass


class OutputValidationError(ValidationError):
    """Raised when output validation fails"""
    pass


# Cache Errors
class CacheError(RAGException):
    """Base exception for cache-related errors"""
    pass


# Security Errors
class SecurityError(RAGException):
    """Base exception for security-related errors"""
    pass


class RateLimitExceededError(SecurityError):
    """Raised when rate limit is exceeded"""
    pass


class UnauthorizedError(SecurityError):
    """Raised when access is unauthorized"""
    pass


# Monitoring Errors
class MonitoringError(RAGException):
    """Base exception for monitoring-related errors"""
    pass


class MetricError(MonitoringError):
    """Raised when metric recording fails"""
    pass


class TracingError(MonitoringError):
    """Raised when tracing fails"""
    pass
