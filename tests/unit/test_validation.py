"""Unit tests for validation"""

import pytest
from src.utils.validation import validate_query
from src.core.exceptions import InputValidationError


class TestValidation:
    """Test input validation"""

    def test_valid_query(self):
        """Test valid query"""
        query = "What is the main contribution?"
        result = validate_query(query)
        assert result == query

    def test_empty_query(self):
        """Test empty query"""
        with pytest.raises(InputValidationError):
            validate_query("")

    def test_too_long_query(self):
        """Test query exceeding max length"""
        with pytest.raises(InputValidationError):
            validate_query("a" * 10001)

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        with pytest.raises(InputValidationError):
            validate_query("test; DROP TABLE users")
