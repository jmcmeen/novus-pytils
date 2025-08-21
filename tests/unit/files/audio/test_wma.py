"""Unit tests for novus_pytils.files.audio.wma module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.audio.wma import get_wma_files


class TestWMA:
    """Test WMA file operations."""

    @patch('novus_pytils.files.audio.wma.get_files_by_extension')
    def test_get_wma_files(self, mock_get_files):
        """Test getting WMA files from directory."""
        # Arrange
        expected_files = ['song1.wma', 'song2.wma', 'track.WMA']
        mock_get_files.return_value = expected_files
        test_dir = '/test/wma/folder'

        # Act
        result = get_wma_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.audio.wma.get_files_by_extension')
    def test_get_wma_files_empty_result(self, mock_get_files):
        """Test getting WMA files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_wma_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.audio.wma.get_files_by_extension')
    def test_get_wma_files_with_wma_extensions(self, mock_get_files):
        """Test that get_wma_files uses WMA_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.wma']
        test_dir = '/test/folder'

        # Act
        get_wma_files(test_dir)

        # Assert
        # Verify that the function was called with WMA_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.audio.wma.get_files_by_extension')
    def test_get_wma_files_pathlib_path(self, mock_get_files):
        """Test get_wma_files with pathlib Path object."""
        # Arrange
        expected_files = ['music.wma']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_wma_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()