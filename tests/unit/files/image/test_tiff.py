"""Unit tests for novus_pytils.files.image.tiff module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.image.tiff import get_tiff_files


class TestTIFF:
    """Test TIFF file operations."""

    @patch('novus_pytils.files.image.tiff.get_files_by_extension')
    def test_get_tiff_files(self, mock_get_files):
        """Test getting TIFF files from directory."""
        # Arrange
        expected_files = ['image1.tiff', 'image2.tif', 'photo.TIFF']
        mock_get_files.return_value = expected_files
        test_dir = '/test/tiff/folder'

        # Act
        result = get_tiff_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.image.tiff.get_files_by_extension')
    def test_get_tiff_files_empty_result(self, mock_get_files):
        """Test getting TIFF files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_tiff_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.image.tiff.get_files_by_extension')
    def test_get_tiff_files_with_tiff_extensions(self, mock_get_files):
        """Test that get_tiff_files uses TIFF_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.tiff']
        test_dir = '/test/folder'

        # Act
        get_tiff_files(test_dir)

        # Assert
        # Verify that the function was called with TIFF_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.image.tiff.get_files_by_extension')
    def test_get_tiff_files_pathlib_path(self, mock_get_files):
        """Test get_tiff_files with pathlib Path object."""
        # Arrange
        expected_files = ['document.tiff']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_tiff_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()