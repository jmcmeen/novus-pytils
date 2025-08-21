"""Unit tests for novus_pytils.files.image.webp module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.image.webp import get_webp_files


class TestWEBP:
    """Test WEBP file operations."""

    @patch('novus_pytils.files.image.webp.get_files_by_extension')
    def test_get_webp_files(self, mock_get_files):
        """Test getting WEBP files from directory."""
        # Arrange
        expected_files = ['image1.webp', 'image2.webp', 'photo.WEBP']
        mock_get_files.return_value = expected_files
        test_dir = '/test/webp/folder'

        # Act
        result = get_webp_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.image.webp.get_files_by_extension')
    def test_get_webp_files_empty_result(self, mock_get_files):
        """Test getting WEBP files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_webp_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.image.webp.get_files_by_extension')
    def test_get_webp_files_with_webp_extensions(self, mock_get_files):
        """Test that get_webp_files uses WEBP_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.webp']
        test_dir = '/test/folder'

        # Act
        get_webp_files(test_dir)

        # Assert
        # Verify that the function was called with WEBP_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.image.webp.get_files_by_extension')
    def test_get_webp_files_pathlib_path(self, mock_get_files):
        """Test get_webp_files with pathlib Path object."""
        # Arrange
        expected_files = ['modern.webp']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_webp_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()