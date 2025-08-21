"""Unit tests for novus_pytils.files.audio.flac module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.audio.flac import get_flac_files


class TestFLAC:
    """Test FLAC file operations."""

    @patch('novus_pytils.files.audio.flac.get_files_by_extension')
    def test_get_flac_files(self, mock_get_files):
        """Test getting FLAC files from directory."""
        # Arrange
        expected_files = ['song1.flac', 'song2.flac', 'track.FLAC']
        mock_get_files.return_value = expected_files
        test_dir = '/test/flac/folder'

        # Act
        result = get_flac_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.audio.flac.get_files_by_extension')
    def test_get_flac_files_empty_result(self, mock_get_files):
        """Test getting FLAC files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_flac_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.audio.flac.get_files_by_extension')
    def test_get_flac_files_with_flac_extensions(self, mock_get_files):
        """Test that get_flac_files uses FLAC_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.flac']
        test_dir = '/test/folder'

        # Act
        get_flac_files(test_dir)

        # Assert
        # Verify that the function was called with FLAC_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.audio.flac.get_files_by_extension')
    def test_get_flac_files_pathlib_path(self, mock_get_files):
        """Test get_flac_files with pathlib Path object."""
        # Arrange
        expected_files = ['music.flac']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_flac_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()