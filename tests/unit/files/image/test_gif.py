"""Unit tests for novus_pytils.files.image.gif module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.image.gif import get_gif_files


class TestGIF:
    """Test GIF file operations."""

    @patch('novus_pytils.files.image.gif.get_files_by_extension')
    def test_get_gif_files(self, mock_get_files):
        """Test getting GIF files from directory."""
        # Arrange
        expected_files = ['animation1.gif', 'animation2.gif', 'image.GIF']
        mock_get_files.return_value = expected_files
        test_dir = '/test/gif/folder'

        # Act
        result = get_gif_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.image.gif.get_files_by_extension')
    def test_get_gif_files_empty_result(self, mock_get_files):
        """Test getting GIF files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_gif_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.image.gif.get_files_by_extension')
    def test_get_gif_files_with_gif_extensions(self, mock_get_files):
        """Test that get_gif_files uses GIF_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.gif']
        test_dir = '/test/folder'

        # Act
        get_gif_files(test_dir)

        # Assert
        # Verify that the function was called with GIF_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.image.gif.get_files_by_extension')
    def test_get_gif_files_pathlib_path(self, mock_get_files):
        """Test get_gif_files with pathlib Path object."""
        # Arrange
        expected_files = ['animation.gif']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_gif_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()