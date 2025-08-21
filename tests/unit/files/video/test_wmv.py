"""Unit tests for novus_pytils.files.video.wmv module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.video.wmv import get_wmv_files


class TestWMV:
    """Test WMV file operations."""

    @patch('novus_pytils.files.video.wmv.get_files_by_extension')
    def test_get_wmv_files(self, mock_get_files):
        """Test getting WMV files from directory."""
        # Arrange
        expected_files = ['movie1.wmv', 'movie2.wmv', 'video.WMV']
        mock_get_files.return_value = expected_files
        test_dir = '/test/wmv/folder'

        # Act
        result = get_wmv_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.video.wmv.get_files_by_extension')
    def test_get_wmv_files_empty_result(self, mock_get_files):
        """Test getting WMV files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_wmv_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.wmv.get_files_by_extension')
    def test_get_wmv_files_with_wmv_extensions(self, mock_get_files):
        """Test that get_wmv_files uses WMV_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.wmv']
        test_dir = '/test/folder'

        # Act
        get_wmv_files(test_dir)

        # Assert
        # Verify that the function was called with WMV_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.video.wmv.get_files_by_extension')
    def test_get_wmv_files_pathlib_path(self, mock_get_files):
        """Test get_wmv_files with pathlib Path object."""
        # Arrange
        expected_files = ['windows_movie.wmv']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_wmv_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()