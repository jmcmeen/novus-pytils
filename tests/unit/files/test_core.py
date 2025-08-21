"""Unit tests for novus_pytils.files.core module."""
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
import tempfile

from novus_pytils.files.core import read_file_bytes, read_file_text


class TestFileCore:
    """Test core file functionality."""

    def test_read_file_bytes(self):
        """Test reading file contents as bytes."""
        # Arrange
        test_content = b'test binary content'
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Act
            result = read_file_bytes(temp_file_path)

            # Assert
            assert result == test_content
            assert isinstance(result, bytes)
        finally:
            # Cleanup
            Path(temp_file_path).unlink()

    @patch('builtins.open', new_callable=mock_open, read_data=b'mock binary data')
    def test_read_file_bytes_mock(self, mock_file):
        """Test reading file bytes with mock."""
        # Act
        result = read_file_bytes('/test/path')

        # Assert
        assert result == b'mock binary data'
        mock_file.assert_called_once_with('/test/path', 'rb')

    def test_read_file_text_default_encoding(self):
        """Test reading file contents as text with default encoding."""
        # Arrange
        test_content = 'test text content'
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Act
            result = read_file_text(temp_file_path)

            # Assert
            assert result == test_content
            assert isinstance(result, str)
        finally:
            # Cleanup
            Path(temp_file_path).unlink()

    def test_read_file_text_custom_encoding(self):
        """Test reading file contents as text with custom encoding."""
        # Arrange
        test_content = 'test text with special chars: ñáéíóú'
        with tempfile.NamedTemporaryFile(mode='w', encoding='latin1', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Act
            result = read_file_text(temp_file_path, encoding='latin1')

            # Assert
            assert result == test_content
            assert isinstance(result, str)
        finally:
            # Cleanup
            Path(temp_file_path).unlink()

    @patch('builtins.open', new_callable=mock_open, read_data='mock text data')
    def test_read_file_text_mock(self, mock_file):
        """Test reading file text with mock."""
        # Act
        result = read_file_text('/test/path')

        # Assert
        assert result == 'mock text data'
        mock_file.assert_called_once_with('/test/path', 'r', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open, read_data='mock text data')
    def test_read_file_text_custom_encoding_mock(self, mock_file):
        """Test reading file text with custom encoding using mock."""
        # Act
        result = read_file_text('/test/path', encoding='latin1')

        # Assert
        assert result == 'mock text data'
        mock_file.assert_called_once_with('/test/path', 'r', encoding='latin1')

    def test_read_file_bytes_file_not_found(self):
        """Test reading bytes from non-existent file."""
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            read_file_bytes('/nonexistent/path')

    def test_read_file_text_file_not_found(self):
        """Test reading text from non-existent file."""
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            read_file_text('/nonexistent/path')

    def test_read_file_bytes_pathlib_path(self):
        """Test reading file bytes with pathlib Path object."""
        # Arrange
        test_content = b'pathlib test content'
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = Path(temp_file.name)

        try:
            # Act
            result = read_file_bytes(temp_file_path)

            # Assert
            assert result == test_content
        finally:
            # Cleanup
            temp_file_path.unlink()

    def test_read_file_text_pathlib_path(self):
        """Test reading file text with pathlib Path object."""
        # Arrange
        test_content = 'pathlib text content'
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = Path(temp_file.name)

        try:
            # Act
            result = read_file_text(temp_file_path)

            # Assert
            assert result == test_content
        finally:
            # Cleanup
            temp_file_path.unlink()