"""Input validation and security"""

import re
from typing import Any
from src.core.exceptions import InputValidationError

def validate_query(query: str, max_length: int = 10000) -> str:
    """Validate and sanitize query input"""
    if not query or not query.strip():
        raise InputValidationError("Query cannot be empty")

    if len(query) > max_length:
        raise InputValidationError(f"Query too long (max {max_length} chars)")

    # Basic SQL injection prevention
    dangerous_patterns = [r';.*drop', r';.*delete', r';.*insert', r';.*update']
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise InputValidationError("Query contains potentially dangerous content")

    return query.strip()
