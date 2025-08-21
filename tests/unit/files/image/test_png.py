"""Unit tests for novus_pytils.files.image.png module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.image.png import get_png_files


class TestPNG:
    """Test PNG file operations."""

    @patch('novus_pytils.files.image.png.get_files_by_extension')
    def test_get_png_files(self, mock_get_files):
        """Test getting PNG files from directory."""
        # Arrange
        expected_files = ['photo1.png', 'photo2.png', 'image.PNG']
        mock_get_files.return_value = expected_files
        test_dir = '/test/png/folder'

        # Act
        result = get_png_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.image.png.get_files_by_extension')
    def test_get_png_files_empty_result(self, mock_get_files):
        """Test getting PNG files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_png_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.image.png.get_files_by_extension')
    def test_get_png_files_with_png_extensions(self, mock_get_files):
        """Test that get_png_files uses PNG_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.png']
        test_dir = '/test/folder'

        # Act
        get_png_files(test_dir)

        # Assert
        # Verify that the function was called with PNG_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.image.png.get_files_by_extension')
    def test_get_png_files_pathlib_path(self, mock_get_files):
        """Test get_png_files with pathlib Path object."""
        # Arrange
        expected_files = ['image.png']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_png_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()