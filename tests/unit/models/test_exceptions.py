"""Unit tests for core.base module."""
import pytest
from unittest.mock import patch
import os

from novus_pytils.models.exceptions import (
    FileHandlerError, UnsupportedFormatError,
    ValidationError
)

class TestExceptions:
    """Test custom exception classes."""
    
    def test_file_handler_error(self):
        """Test FileHandlerError exception."""
        error = FileHandlerError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_unsupported_format_error(self):
        """Test UnsupportedFormatError exception."""
        error = UnsupportedFormatError("Unsupported format: .xyz")
        assert str(error) == "Unsupported format: .xyz"
        assert isinstance(error, FileHandlerError)
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, FileHandlerError)
