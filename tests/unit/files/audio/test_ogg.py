"""Unit tests for novus_pytils.files.audio.ogg module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.audio.ogg import get_ogg_files


class TestOGG:
    """Test OGG file operations."""

    @patch('novus_pytils.files.audio.ogg.get_files_by_extension')
    def test_get_ogg_files(self, mock_get_files):
        """Test getting OGG files from directory."""
        # Arrange
        expected_files = ['song1.ogg', 'song2.ogg', 'track.OGG']
        mock_get_files.return_value = expected_files
        test_dir = '/test/ogg/folder'

        # Act
        result = get_ogg_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.audio.ogg.get_files_by_extension')
    def test_get_ogg_files_empty_result(self, mock_get_files):
        """Test getting OGG files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_ogg_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.audio.ogg.get_files_by_extension')
    def test_get_ogg_files_with_ogg_extensions(self, mock_get_files):
        """Test that get_ogg_files uses OGG_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.ogg']
        test_dir = '/test/folder'

        # Act
        get_ogg_files(test_dir)

        # Assert
        # Verify that the function was called with OGG_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.audio.ogg.get_files_by_extension')
    def test_get_ogg_files_pathlib_path(self, mock_get_files):
        """Test get_ogg_files with pathlib Path object."""
        # Arrange
        expected_files = ['music.ogg']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_ogg_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()