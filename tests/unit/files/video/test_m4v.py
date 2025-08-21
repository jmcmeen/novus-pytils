"""Unit tests for novus_pytils.files.video.m4v module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.video.m4v import get_m4v_files


class TestM4V:
    """Test M4V file operations."""

    @patch('novus_pytils.files.video.m4v.get_files_by_extension')
    def test_get_m4v_files(self, mock_get_files):
        """Test getting M4V files from directory."""
        # Arrange
        expected_files = ['movie1.m4v', 'movie2.m4v', 'video.M4V']
        mock_get_files.return_value = expected_files
        test_dir = '/test/m4v/folder'

        # Act
        result = get_m4v_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.video.m4v.get_files_by_extension')
    def test_get_m4v_files_empty_result(self, mock_get_files):
        """Test getting M4V files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_m4v_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.m4v.get_files_by_extension')
    def test_get_m4v_files_with_m4v_extensions(self, mock_get_files):
        """Test that get_m4v_files uses M4V_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.m4v']
        test_dir = '/test/folder'

        # Act
        get_m4v_files(test_dir)

        # Assert
        # Verify that the function was called with M4V_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.video.m4v.get_files_by_extension')
    def test_get_m4v_files_pathlib_path(self, mock_get_files):
        """Test get_m4v_files with pathlib Path object."""
        # Arrange
        expected_files = ['itunes_movie.m4v']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_m4v_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()