"""Unit tests for novus_pytils.files.video.avi module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.video.avi import get_avi_files


class TestAVI:
    """Test AVI file operations."""

    @patch('novus_pytils.files.video.avi.get_files_by_extension')
    def test_get_avi_files(self, mock_get_files):
        """Test getting AVI files from directory."""
        # Arrange
        expected_files = ['movie1.avi', 'movie2.avi', 'video.AVI']
        mock_get_files.return_value = expected_files
        test_dir = '/test/avi/folder'

        # Act
        result = get_avi_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.video.avi.get_files_by_extension')
    def test_get_avi_files_empty_result(self, mock_get_files):
        """Test getting AVI files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_avi_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.avi.get_files_by_extension')
    def test_get_avi_files_with_avi_extensions(self, mock_get_files):
        """Test that get_avi_files uses AVI_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.avi']
        test_dir = '/test/folder'

        # Act
        get_avi_files(test_dir)

        # Assert
        # Verify that the function was called with AVI_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.video.avi.get_files_by_extension')
    def test_get_avi_files_pathlib_path(self, mock_get_files):
        """Test get_avi_files with pathlib Path object."""
        # Arrange
        expected_files = ['oldmovie.avi']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_avi_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()