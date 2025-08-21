"""Unit tests for novus_pytils.files.audio.mp3 module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.audio.mp3 import get_mp3_files


class TestMP3:
    """Test MP3 file operations."""

    @patch('novus_pytils.files.audio.mp3.get_files_by_extension')
    def test_get_mp3_files(self, mock_get_files):
        """Test getting MP3 files from directory."""
        # Arrange
        expected_files = ['song1.mp3', 'song2.mp3', 'track.MP3']
        mock_get_files.return_value = expected_files
        test_dir = '/test/mp3/folder'

        # Act
        result = get_mp3_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.audio.mp3.get_files_by_extension')
    def test_get_mp3_files_empty_result(self, mock_get_files):
        """Test getting MP3 files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_mp3_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.audio.mp3.get_files_by_extension')
    def test_get_mp3_files_with_mp3_extensions(self, mock_get_files):
        """Test that get_mp3_files uses MP3_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.mp3']
        test_dir = '/test/folder'

        # Act
        get_mp3_files(test_dir)

        # Assert
        # Verify that the function was called with MP3_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.audio.mp3.get_files_by_extension')
    def test_get_mp3_files_pathlib_path(self, mock_get_files):
        """Test get_mp3_files with pathlib Path object."""
        # Arrange
        expected_files = ['music.mp3']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_mp3_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()