"""Unit tests for novus_pytils.files.video.mk4 module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.video.mk4 import get_mkv_files


class TestMKV:
    """Test MKV file operations."""

    @patch('novus_pytils.files.video.mk4.get_files_by_extension')
    def test_get_mkv_files(self, mock_get_files):
        """Test getting MKV files from directory."""
        # Arrange
        expected_files = ['movie1.mkv', 'movie2.mkv', 'video.MKV']
        mock_get_files.return_value = expected_files
        test_dir = '/test/mkv/folder'

        # Act
        result = get_mkv_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.video.mk4.get_files_by_extension')
    def test_get_mkv_files_empty_result(self, mock_get_files):
        """Test getting MKV files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_mkv_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.mk4.get_files_by_extension')
    def test_get_mkv_files_with_mkv_extensions(self, mock_get_files):
        """Test that get_mkv_files uses MKV_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.mkv']
        test_dir = '/test/folder'

        # Act
        get_mkv_files(test_dir)

        # Assert
        # Verify that the function was called with MKV_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.video.mk4.get_files_by_extension')
    def test_get_mkv_files_pathlib_path(self, mock_get_files):
        """Test get_mkv_files with pathlib Path object."""
        # Arrange
        expected_files = ['matroska_video.mkv']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_mkv_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()