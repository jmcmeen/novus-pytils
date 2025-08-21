"""Unit tests for novus_pytils.files.text.core module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.text.core import count_text_files, get_text_files


class TestTextCore:
    """Test core text functionality."""

    @patch('novus_pytils.files.text.core.get_files_by_extension')
    def test_count_text_files(self, mock_get_files):
        """Test counting text files in a folder."""
        # Arrange
        mock_get_files.return_value = [
            'document.txt',
            'readme.md',
            'config.json',
            'data.csv'
        ]
        test_path = '/test/text/folder'

        # Act
        result = count_text_files(test_path)

        # Assert
        assert result == 4
        mock_get_files.assert_called_once_with(test_path, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.text.core.get_files_by_extension')
    def test_count_text_files_empty_folder(self, mock_get_files):
        """Test counting text files in empty folder."""
        # Arrange
        mock_get_files.return_value = []
        test_path = '/test/empty/folder'

        # Act
        result = count_text_files(test_path)

        # Assert
        assert result == 0
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.text.core.get_files_by_extension')
    def test_get_text_files_default_extensions(self, mock_get_files):
        """Test getting text files with default extensions."""
        # Arrange
        expected_files = ['docs/readme.md', 'docs/config.json', 'docs/data.csv']
        mock_get_files.return_value = expected_files
        test_dir = '/test/text/folder'

        # Act
        result = get_text_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1], relative=True)

    @patch('novus_pytils.files.text.core.get_files_by_extension')
    def test_get_text_files_custom_extensions(self, mock_get_files):
        """Test getting text files with custom extensions."""
        # Arrange
        custom_extensions = ['.txt', '.md']
        expected_files = ['document.txt', 'readme.md']
        mock_get_files.return_value = expected_files
        test_dir = '/test/custom/folder'

        # Act
        result = get_text_files(test_dir, custom_extensions)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, custom_extensions, relative=True)

    @patch('novus_pytils.files.text.core.get_files_by_extension')
    def test_get_text_files_empty_result(self, mock_get_files):
        """Test getting text files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/no/text'

        # Act
        result = get_text_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.text.core.get_files_by_extension')
    def test_get_text_files_with_supported_extensions(self, mock_get_files):
        """Test that get_text_files uses SUPPORTED_TEXT_EXTENSIONS by default."""
        # Arrange
        mock_get_files.return_value = ['test.txt']
        test_dir = '/test/folder'

        # Act
        get_text_files(test_dir)

        # Assert
        # Verify that the function was called with SUPPORTED_TEXT_EXTENSIONS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory
        assert call_args[1]['relative'] is True  # relative=True keyword argument

    @patch('novus_pytils.files.text.core.get_files_by_extension')
    def test_count_text_files_with_supported_extensions(self, mock_get_files):
        """Test that count_text_files uses SUPPORTED_TEXT_EXTENSIONS."""
        # Arrange
        mock_get_files.return_value = ['a.txt', 'b.md', 'c.json']
        test_path = '/test/path'

        # Act
        count_text_files(test_path)

        # Assert
        # Verify that the function was called with SUPPORTED_TEXT_EXTENSIONS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_path  # First argument is the directory

    @patch('novus_pytils.files.text.core.get_files_by_extension')
    def test_get_text_files_pathlib_path(self, mock_get_files):
        """Test get_text_files with pathlib Path object."""
        # Arrange
        expected_files = ['document.txt']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_text_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.text.core.get_files_by_extension')
    def test_count_text_files_pathlib_path(self, mock_get_files):
        """Test count_text_files with pathlib Path object."""
        # Arrange
        mock_get_files.return_value = ['a.txt', 'b.md']
        test_path = Path('/test/pathlib/path')

        # Act
        result = count_text_files(test_path)

        # Assert
        assert result == 2
        mock_get_files.assert_called_once()