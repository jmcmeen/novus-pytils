"""Unit tests for core.base module."""
import pytest
from unittest.mock import patch
import os

from novus_pytils.core.exceptions import (
    FileHandlerError, UnsupportedFormatError,
    ValidationError
)

from novus_pytils.core.models import BaseFileHandler


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


class TestBaseFileHandler:
    """Test BaseFileHandler abstract class."""
    
    def test_cannot_instantiate_directly(self):
        """Test that BaseFileHandler cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseFileHandler()
    
    def test_subclass_must_implement_abstract_methods(self):
        """Test that subclasses must implement abstract methods."""
        
        class IncompleteHandler(BaseFileHandler):
            pass
        
        with pytest.raises(TypeError):
            IncompleteHandler()
    
    def test_complete_subclass_can_be_instantiated(self):
        """Test that complete subclass can be instantiated."""
        
        class CompleteHandler(BaseFileHandler):
            def read(self, file_path, **kwargs):
                return "content"
            
            def write(self, file_path, content, **kwargs):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                return True
        
        # Should not raise exception
        handler = CompleteHandler()
        assert isinstance(handler, BaseFileHandler)
    
    @patch('os.path.exists')
    @patch('os.stat')
    def test_subclass_methods_work(self, mock_stat, mock_exists):
        """Test that BaseFileHandler methods work correctly."""
        
        class TestHandler(BaseFileHandler):
            def read(self, file_path, **kwargs):
                return "content"
            
            def write(self, file_path, content, **kwargs):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                if target_format == ".xyz":
                    return False
                return True
        
        handler = TestHandler()
        handler.supported_extensions = [".txt", ".pdf"]
        handler.conversion_map = {".txt": [".pdf", ".docx", ".html"]}
        
        # Test validate_file method
        mock_exists.return_value = True
        assert handler.validate_file("test.txt") is True
        
        mock_exists.return_value = False
        assert handler.validate_file("test.txt") is False
        
        # Test with unsupported extension
        mock_exists.return_value = True
        assert handler.validate_file("test.xyz") is False
        
        # Test convert method (implemented by subclass)
        assert handler.convert("input.txt", "output.pdf", ".pdf") is True
        assert handler.convert("input.txt", "output.xyz", ".xyz") is False
        
        # Test get_metadata method
        stat_result = type('StatResult', (), {
            'st_size': 1024,
            'st_ctime': 1234567890,
            'st_mtime': 1234567891,
            'st_atime': 1234567892
        })()
        mock_stat.return_value = stat_result
        mock_exists.return_value = True
        
        metadata = handler.get_metadata("test.txt")
        assert metadata["size"] == 1024
        assert metadata["extension"] == ".txt"
        assert metadata["basename"] == "test.txt"
        
        # Test get_supported_conversions method
        conversions = handler.get_supported_conversions(".txt")
        assert ".pdf" in conversions
        assert ".docx" in conversions
        assert ".html" in conversions
        
        conversions = handler.get_supported_conversions(".unknown")
        assert conversions == []


class TestBaseFileHandlerMethods:
    """Test BaseFileHandler actual methods."""
    
    def setup_method(self):
        """Setup test handler."""
        class TestHandler(BaseFileHandler):
            def read(self, file_path, **kwargs):
                return "content"
            
            def write(self, file_path, content, **kwargs):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                return True
        
        self.handler = TestHandler()
    
    @patch('os.path.exists')
    def test_validate_file_exists_and_supported(self, mock_exists):
        """Test file validation when file exists and is supported."""
        mock_exists.return_value = True
        self.handler.supported_extensions = ['.txt']
        
        result = self.handler.validate_file("existing_file.txt")
        assert result is True
        mock_exists.assert_called_once_with("existing_file.txt")
    
    @patch('os.path.exists')
    def test_validate_file_not_exists(self, mock_exists):
        """Test file validation when file doesn't exist."""
        mock_exists.return_value = False
        self.handler.supported_extensions = ['.txt']
        
        result = self.handler.validate_file("nonexistent_file.txt")
        assert result is False
    
    @patch('os.path.exists')  
    def test_validate_file_unsupported_extension(self, mock_exists):
        """Test file validation with unsupported extension."""
        mock_exists.return_value = True
        self.handler.supported_extensions = ['.txt', '.pdf']
        
        result = self.handler.validate_file("document.xyz")
        assert result is False
    
    def test_get_supported_conversions(self):
        """Test getting supported conversions."""
        self.handler.conversion_map = {".txt": [".pdf", ".docx"], ".jpg": [".png", ".gif"]}
        
        conversions = self.handler.get_supported_conversions(".txt")
        assert ".pdf" in conversions
        assert ".docx" in conversions
        
        conversions = self.handler.get_supported_conversions(".unknown")
        assert conversions == []
    
    @patch('os.stat')
    @patch('os.path.exists')
    def test_get_metadata_success(self, mock_exists, mock_stat):
        """Test getting file metadata successfully."""
        mock_exists.return_value = True
        
        stat_result = type('StatResult', (), {
            'st_size': 1024,
            'st_ctime': 1234567890,
            'st_mtime': 1234567891,
            'st_atime': 1234567892
        })()
        mock_stat.return_value = stat_result
        
        metadata = self.handler.get_metadata("test.txt")
        
        assert metadata['size'] == 1024
        assert metadata['extension'] == '.txt'
        assert metadata['basename'] == 'test.txt'
        assert 'created' in metadata
        assert 'modified' in metadata
        assert 'accessed' in metadata
    
    @patch('os.path.exists')
    def test_get_metadata_file_not_exists(self, mock_exists):
        """Test getting metadata for nonexistent file."""
        mock_exists.return_value = False
        
        with pytest.raises(FileHandlerError):
            self.handler.get_metadata("nonexistent.txt")