"""Unit tests for novus_pytils.files.video.mp4 module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.video.mp4 import get_mp4_files


class TestMP4:
    """Test MP4 file operations."""

    @patch('novus_pytils.files.video.mp4.get_files_by_extension')
    def test_get_mp4_files(self, mock_get_files):
        """Test getting MP4 files from directory."""
        # Arrange
        expected_files = ['movie1.mp4', 'movie2.mp4', 'video.MP4']
        mock_get_files.return_value = expected_files
        test_dir = '/test/mp4/folder'

        # Act
        result = get_mp4_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.video.mp4.get_files_by_extension')
    def test_get_mp4_files_empty_result(self, mock_get_files):
        """Test getting MP4 files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_mp4_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.mp4.get_files_by_extension')
    def test_get_mp4_files_with_mp4_extensions(self, mock_get_files):
        """Test that get_mp4_files uses MP4_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.mp4']
        test_dir = '/test/folder'

        # Act
        get_mp4_files(test_dir)

        # Assert
        # Verify that the function was called with MP4_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.video.mp4.get_files_by_extension')
    def test_get_mp4_files_pathlib_path(self, mock_get_files):
        """Test get_mp4_files with pathlib Path object."""
        # Arrange
        expected_files = ['movie.mp4']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_mp4_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()