"""Input validation utilities for the RAG system."""

from pathlib import Path
from typing import List, Optional

from src.core.exceptions import InputValidationError


def validate_query(query: str, max_length: int = 10000) -> str:
    """Validate and sanitize a user query.

    Args:
        query: The raw query string.
        max_length: Maximum allowed character length.

    Returns:
        The stripped query string.

    Raises:
        InputValidationError: If validation fails.
    """
    if not query or not query.strip():
        raise InputValidationError("Query cannot be empty")

    if len(query) > max_length:
        raise InputValidationError(f"Query too long (max {max_length} chars)")

    return query.strip()


def validate_file_path(
    path: str,
    allowed_extensions: Optional[List[str]] = None,
    max_size_bytes: Optional[int] = None,
) -> Path:
    """Validate that a file path exists, has an allowed extension, and is within size limits.

    Args:
        path: File path to validate.
        allowed_extensions: List of allowed extensions (e.g. [".pdf", ".txt"]).
            If None, all extensions are accepted.
        max_size_bytes: Maximum file size in bytes. If None, no limit is enforced.

    Returns:
        Resolved Path object.

    Raises:
        InputValidationError: If validation fails.
    """
    resolved = Path(path).resolve()

    if not resolved.exists():
        raise InputValidationError(f"File not found: {path}")

    if not resolved.is_file():
        raise InputValidationError(f"Path is not a file: {path}")

    if allowed_extensions is not None:
        ext = resolved.suffix.lower()
        allowed_lower = [e.lower() for e in allowed_extensions]
        if ext not in allowed_lower:
            raise InputValidationError(
                f"Unsupported file type '{ext}'. Allowed: {allowed_extensions}"
            )

    if max_size_bytes is not None:
        size = resolved.stat().st_size
        if size > max_size_bytes:
            raise InputValidationError(
                f"File too large ({size} bytes). Maximum: {max_size_bytes} bytes"
            )

    return resolved


def validate_file_type(path: str, allowed_extensions: List[str]) -> bool:
    """Check whether a file has one of the allowed extensions.

    Args:
        path: File path to check.
        allowed_extensions: List of allowed extensions (e.g. [".pdf", ".txt"]).

    Returns:
        True if the file extension is in the allowed list.
    """
    ext = Path(path).suffix.lower()
    return ext in [e.lower() for e in allowed_extensions]
