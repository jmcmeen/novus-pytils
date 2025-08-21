"""Unit tests for core.base module."""

from novus_pytils.models.exceptions import (
    FileHandlerError, UnsupportedFormatError, ConversionError,
    ValidationError, SecurityError, WAVError, InvalidWAVFormatError,
    CorruptedFileError
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
    
    def test_conversion_error(self):
        """Test ConversionError exception."""
        error = ConversionError("Conversion failed")
        assert str(error) == "Conversion failed"
        assert isinstance(error, FileHandlerError)
    
    def test_security_error(self):
        """Test SecurityError exception."""
        error = SecurityError("Security check failed")
        assert str(error) == "Security check failed"
        assert isinstance(error, FileHandlerError)
    
    def test_wav_error(self):
        """Test WAVError exception."""
        error = WAVError("WAV parsing error")
        assert str(error) == "WAV parsing error"
        assert isinstance(error, Exception)
    
    def test_invalid_wav_format_error(self):
        """Test InvalidWAVFormatError exception."""
        error = InvalidWAVFormatError("Invalid WAV format")
        assert str(error) == "Invalid WAV format"
        assert isinstance(error, WAVError)
    
    def test_corrupted_file_error(self):
        """Test CorruptedFileError exception."""
        error = CorruptedFileError("File is corrupted")
        assert str(error) == "File is corrupted"
        assert isinstance(error, WAVError)
