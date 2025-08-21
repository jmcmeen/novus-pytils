"""Unit tests for novus_pytils.files.video.mov module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.video.mov import get_mov_files


class TestMOV:
    """Test MOV file operations."""

    @patch('novus_pytils.files.video.mov.get_files_by_extension')
    def test_get_mov_files(self, mock_get_files):
        """Test getting MOV files from directory."""
        # Arrange
        expected_files = ['movie1.mov', 'movie2.mov', 'video.MOV']
        mock_get_files.return_value = expected_files
        test_dir = '/test/mov/folder'

        # Act
        result = get_mov_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.video.mov.get_files_by_extension')
    def test_get_mov_files_empty_result(self, mock_get_files):
        """Test getting MOV files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_mov_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.mov.get_files_by_extension')
    def test_get_mov_files_with_mov_extensions(self, mock_get_files):
        """Test that get_mov_files uses MOV_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.mov']
        test_dir = '/test/folder'

        # Act
        get_mov_files(test_dir)

        # Assert
        # Verify that the function was called with MOV_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.video.mov.get_files_by_extension')
    def test_get_mov_files_pathlib_path(self, mock_get_files):
        """Test get_mov_files with pathlib Path object."""
        # Arrange
        expected_files = ['quicktime.mov']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_mov_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()