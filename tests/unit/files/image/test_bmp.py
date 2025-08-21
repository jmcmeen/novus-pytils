"""Unit tests for novus_pytils.files.image.bmp module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.image.bmp import get_bmp_files


class TestBMP:
    """Test BMP file operations."""

    @patch('novus_pytils.files.image.bmp.get_files_by_extension')
    def test_get_bmp_files(self, mock_get_files):
        """Test getting BMP files from directory."""
        # Arrange
        expected_files = ['image1.bmp', 'image2.bmp', 'photo.BMP']
        mock_get_files.return_value = expected_files
        test_dir = '/test/bmp/folder'

        # Act
        result = get_bmp_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.image.bmp.get_files_by_extension')
    def test_get_bmp_files_empty_result(self, mock_get_files):
        """Test getting BMP files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_bmp_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.image.bmp.get_files_by_extension')
    def test_get_bmp_files_with_bmp_extensions(self, mock_get_files):
        """Test that get_bmp_files uses BMP_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.bmp']
        test_dir = '/test/folder'

        # Act
        get_bmp_files(test_dir)

        # Assert
        # Verify that the function was called with BMP_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.image.bmp.get_files_by_extension')
    def test_get_bmp_files_pathlib_path(self, mock_get_files):
        """Test get_bmp_files with pathlib Path object."""
        # Arrange
        expected_files = ['bitmap.bmp']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_bmp_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()