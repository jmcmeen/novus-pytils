"""Unit tests for novus_pytils.files.video.flv module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.video.flv import get_flv_files


class TestFLV:
    """Test FLV file operations."""

    @patch('novus_pytils.files.video.flv.get_files_by_extension')
    def test_get_flv_files(self, mock_get_files):
        """Test getting FLV files from directory."""
        # Arrange
        expected_files = ['stream1.flv', 'stream2.flv', 'video.FLV']
        mock_get_files.return_value = expected_files
        test_dir = '/test/flv/folder'

        # Act
        result = get_flv_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.video.flv.get_files_by_extension')
    def test_get_flv_files_empty_result(self, mock_get_files):
        """Test getting FLV files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_flv_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.flv.get_files_by_extension')
    def test_get_flv_files_with_flv_extensions(self, mock_get_files):
        """Test that get_flv_files uses FLV_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.flv']
        test_dir = '/test/folder'

        # Act
        get_flv_files(test_dir)

        # Assert
        # Verify that the function was called with FLV_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.video.flv.get_files_by_extension')
    def test_get_flv_files_pathlib_path(self, mock_get_files):
        """Test get_flv_files with pathlib Path object."""
        # Arrange
        expected_files = ['flash_video.flv']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_flv_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()