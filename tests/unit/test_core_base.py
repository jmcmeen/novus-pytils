"""Unit tests for core.base module."""
import pytest
from unittest.mock import patch
import os

from novus_pytils.models.exceptions import (
    FileHandlerError, UnsupportedFormatError,
    ValidationError
)

from novus_pytils.models.base import BaseFileHandler


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
                return "test content"
            
            def write(self, file_path, content, **kwargs):
                return True
            
            def create(self, file_path, content=None, **kwargs):
                return True
            
            def update(self, file_path, content, **kwargs):
                return True
            
            def delete(self, file_path):
                return True
            
            def copy(self, src_path, dest_path):
                return True
            
            def move(self, src_path, dest_path):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                return True
            
            def get_metadata(self, file_path):
                return {"size": 1024}
            
            def get_supported_conversions(self, file_extension):
                return [".txt", ".pdf"]
        
        handler = CompleteHandler()
        assert isinstance(handler, BaseFileHandler)
    
    def test_subclass_methods_work(self):
        """Test that subclass methods work correctly."""
        
        class TestHandler(BaseFileHandler):
            def read(self, file_path, **kwargs):
                return f"content of {file_path}"
            
            def write(self, file_path, content, **kwargs):
                return len(content) > 0
            
            def create(self, file_path, content=None, **kwargs):
                return True
            
            def update(self, file_path, content, **kwargs):
                return True
            
            def delete(self, file_path):
                return os.path.exists(file_path)
            
            def copy(self, src_path, dest_path):
                return True
            
            def move(self, src_path, dest_path):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                return target_format in [".pdf", ".txt"]
            
            def get_metadata(self, file_path):
                return {
                    "path": file_path,
                    "size": 1024,
                    "extension": os.path.splitext(file_path)[1]
                }
            
            def get_supported_conversions(self, file_extension):
                conversions = {
                    ".txt": [".pdf", ".docx", ".html"],
                    ".jpg": [".png", ".gif", ".bmp"],
                    ".mp3": [".wav", ".ogg", ".flac"]
                }
                return conversions.get(file_extension, [])
        
        handler = TestHandler()
        
        # Test read method
        assert handler.read("test.txt") == "content of test.txt"
        
        # Test write method
        assert handler.write("test.txt", "content") is True
        assert handler.write("test.txt", "") is False
        
        # Test create method
        assert handler.create("test.txt", "content") is True
        
        # Test update method
        assert handler.update("test.txt", "new content") is True
        
        # Test convert method
        assert handler.convert("input.txt", "output.pdf", ".pdf") is True
        assert handler.convert("input.txt", "output.xyz", ".xyz") is False
        
        # Test get_metadata method
        metadata = handler.get_metadata("test.txt")
        assert metadata["path"] == "test.txt"
        assert metadata["size"] == 1024
        assert metadata["extension"] == ".txt"
        
        # Test get_supported_conversions method
        conversions = handler.get_supported_conversions(".txt")
        assert ".pdf" in conversions
        assert ".docx" in conversions
        assert ".html" in conversions
        
        conversions = handler.get_supported_conversions(".unknown")
        assert conversions == []


class TestBaseFileHandlerValidation:
    """Test BaseFileHandler validation methods."""
    
    def setup_method(self):
        """Setup test handler."""
        class TestHandler(BaseFileHandler):
            def read(self, file_path, **kwargs):
                return "content"
            
            def write(self, file_path, content, **kwargs):
                return True
            
            def create(self, file_path, content=None, **kwargs):
                return True
            
            def update(self, file_path, content, **kwargs):
                return True
            
            def delete(self, file_path):
                return True
            
            def copy(self, src_path, dest_path):
                return True
            
            def move(self, src_path, dest_path):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                return True
            
            def get_metadata(self, file_path):
                return {}
            
            def get_supported_conversions(self, file_extension):
                return []
        
        self.handler = TestHandler()
    
    @patch('os.path.exists')
    def test_validate_file_exists_true(self, mock_exists):
        """Test file exists validation when file exists."""
        mock_exists.return_value = True
        
        # Should not raise exception
        self.handler._validate_file_exists("existing_file.txt")
        mock_exists.assert_called_once_with("existing_file.txt")
    
    @patch('os.path.exists')
    def test_validate_file_exists_false(self, mock_exists):
        """Test file exists validation when file doesn't exist."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            self.handler._validate_file_exists("nonexistent_file.txt")
    
    def test_validate_file_extension_valid(self):
        """Test file extension validation with valid extensions."""
        valid_extensions = [".txt", ".pdf", ".docx"]
        
        # Should not raise exception
        self.handler._validate_file_extension("document.txt", valid_extensions)
        self.handler._validate_file_extension("document.pdf", valid_extensions)
        self.handler._validate_file_extension("document.docx", valid_extensions)
    
    def test_validate_file_extension_invalid(self):
        """Test file extension validation with invalid extension."""
        valid_extensions = [".txt", ".pdf", ".docx"]
        
        with pytest.raises(UnsupportedFormatError):
            self.handler._validate_file_extension("document.xyz", valid_extensions)
    
    def test_validate_file_extension_case_insensitive(self):
        """Test file extension validation is case insensitive."""
        valid_extensions = [".txt", ".pdf"]
        
        # Should not raise exception
        self.handler._validate_file_extension("document.TXT", valid_extensions)
        self.handler._validate_file_extension("document.PDF", valid_extensions)
    
    def test_validate_content_not_none(self):
        """Test content validation when content is not None."""
        # Should not raise exception
        self.handler._validate_content("some content")
        self.handler._validate_content("")
        self.handler._validate_content(b"binary content")
        self.handler._validate_content({"data": "json"})
    
    def test_validate_content_none(self):
        """Test content validation when content is None."""
        with pytest.raises(ValidationError):
            self.handler._validate_content(None)
    
    @patch('os.path.dirname')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_ensure_directory_exists_already_exists(self, mock_makedirs, mock_exists, mock_dirname):
        """Test ensuring directory exists when it already exists."""
        mock_dirname.return_value = "/existing/directory"
        mock_exists.return_value = True
        
        self.handler._ensure_directory_exists("/existing/directory/file.txt")
        
        mock_dirname.assert_called_once_with("/existing/directory/file.txt")
        mock_exists.assert_called_once_with("/existing/directory")
        mock_makedirs.assert_not_called()
    
    @patch('os.path.dirname')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_ensure_directory_exists_create_new(self, mock_makedirs, mock_exists, mock_dirname):
        """Test ensuring directory exists when it needs to be created."""
        mock_dirname.return_value = "/new/directory"
        mock_exists.return_value = False
        
        self.handler._ensure_directory_exists("/new/directory/file.txt")
        
        mock_dirname.assert_called_once_with("/new/directory/file.txt")
        mock_exists.assert_called_once_with("/new/directory")
        mock_makedirs.assert_called_once_with("/new/directory", exist_ok=True)
    
    def test_get_file_extension(self):
        """Test getting file extension."""
        assert self.handler._get_file_extension("file.txt") == ".txt"
        assert self.handler._get_file_extension("document.PDF") == ".pdf"
        assert self.handler._get_file_extension("archive.tar.gz") == ".gz"
        assert self.handler._get_file_extension("no_extension") == ""
    
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_get_file_size(self, mock_exists, mock_getsize):
        """Test getting file size."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        
        size = self.handler._get_file_size("test.txt")
        
        assert size == 1024
        mock_exists.assert_called_once_with("test.txt")
        mock_getsize.assert_called_once_with("test.txt")
    
    @patch('os.path.exists')
    def test_get_file_size_nonexistent(self, mock_exists):
        """Test getting file size for nonexistent file."""
        mock_exists.return_value = False
        
        size = self.handler._get_file_size("nonexistent.txt")
        
        assert size == 0
        mock_exists.assert_called_once_with("nonexistent.txt")
    
    @patch('os.path.getmtime')
    @patch('os.path.exists')
    def test_get_file_modified_time(self, mock_exists, mock_getmtime):
        """Test getting file modification time."""
        mock_exists.return_value = True
        mock_getmtime.return_value = 1234567890
        
        mtime = self.handler._get_file_modified_time("test.txt")
        
        assert mtime == 1234567890
        mock_exists.assert_called_once_with("test.txt")
        mock_getmtime.assert_called_once_with("test.txt")
    
    @patch('os.path.exists')
    def test_get_file_modified_time_nonexistent(self, mock_exists):
        """Test getting modification time for nonexistent file."""
        mock_exists.return_value = False
        
        mtime = self.handler._get_file_modified_time("nonexistent.txt")
        
        assert mtime is None
        mock_exists.assert_called_once_with("nonexistent.txt")