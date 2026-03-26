"""Unit tests for input validation."""

import os
import tempfile
import pytest
from src.utils.validation import validate_query, validate_file_path, validate_file_type
from src.core.exceptions import InputValidationError


class TestValidateQuery:
    def test_valid_query(self):
        result = validate_query("What is the main contribution?")
        assert result == "What is the main contribution?"

    def test_strips_whitespace(self):
        result = validate_query("  hello  ")
        assert result == "hello"

    def test_empty_query(self):
        with pytest.raises(InputValidationError):
            validate_query("")

    def test_whitespace_only_query(self):
        with pytest.raises(InputValidationError):
            validate_query("   ")

    def test_too_long_query(self):
        with pytest.raises(InputValidationError):
            validate_query("a" * 10001)

    def test_custom_max_length(self):
        with pytest.raises(InputValidationError):
            validate_query("hello", max_length=3)

    def test_at_max_length_ok(self):
        result = validate_query("abc", max_length=3)
        assert result == "abc"


class TestValidateFilePath:
    def test_valid_file(self, tmp_path):
        f = tmp_path / "test.pdf"
        f.write_text("content")
        result = validate_file_path(str(f))
        assert result.exists()

    def test_nonexistent_file(self):
        with pytest.raises(InputValidationError, match="File not found"):
            validate_file_path("/nonexistent/file.pdf")

    def test_directory_rejected(self, tmp_path):
        with pytest.raises(InputValidationError, match="not a file"):
            validate_file_path(str(tmp_path))

    def test_allowed_extension(self, tmp_path):
        f = tmp_path / "test.pdf"
        f.write_text("content")
        result = validate_file_path(str(f), allowed_extensions=[".pdf", ".txt"])
        assert result.suffix == ".pdf"

    def test_disallowed_extension(self, tmp_path):
        f = tmp_path / "test.exe"
        f.write_text("content")
        with pytest.raises(InputValidationError, match="Unsupported file type"):
            validate_file_path(str(f), allowed_extensions=[".pdf"])

    def test_case_insensitive_extension(self, tmp_path):
        f = tmp_path / "test.PDF"
        f.write_text("content")
        result = validate_file_path(str(f), allowed_extensions=[".pdf"])
        assert result.exists()

    def test_max_size_ok(self, tmp_path):
        f = tmp_path / "small.txt"
        f.write_text("hi")
        result = validate_file_path(str(f), max_size_bytes=1_000_000)
        assert result.exists()

    def test_max_size_exceeded(self, tmp_path):
        f = tmp_path / "big.txt"
        f.write_bytes(b"x" * 1000)
        with pytest.raises(InputValidationError, match="File too large"):
            validate_file_path(str(f), max_size_bytes=100)


class TestValidateFileType:
    def test_matching_extension(self):
        assert validate_file_type("paper.pdf", [".pdf", ".txt"]) is True

    def test_non_matching_extension(self):
        assert validate_file_type("image.png", [".pdf", ".txt"]) is False

    def test_case_insensitive(self):
        assert validate_file_type("DOC.PDF", [".pdf"]) is True

    def test_no_extension(self):
        assert validate_file_type("Makefile", [".pdf"]) is False
