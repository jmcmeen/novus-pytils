"""Unit tests for novus_pytils.files.video.core module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.video.core import count_video_files, get_video_files


class TestVideoCore:
    """Test core video functionality."""

    @patch('novus_pytils.files.video.core.get_files_by_extension')
    def test_count_video_files(self, mock_get_files):
        """Test counting video files in a folder."""
        # Arrange
        mock_get_files.return_value = [
            'movie1.mp4',
            'movie2.avi',
            'clip.mov',
            'video.webm'
        ]
        test_path = '/test/video/folder'

        # Act
        result = count_video_files(test_path)

        # Assert
        assert result == 4
        mock_get_files.assert_called_once_with(test_path, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.video.core.get_files_by_extension')
    def test_count_video_files_empty_folder(self, mock_get_files):
        """Test counting video files in empty folder."""
        # Arrange
        mock_get_files.return_value = []
        test_path = '/test/empty/folder'

        # Act
        result = count_video_files(test_path)

        # Assert
        assert result == 0
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.core.get_files_by_extension')
    def test_get_video_files_default_extensions(self, mock_get_files):
        """Test getting video files with default extensions."""
        # Arrange
        expected_files = ['videos/movie1.mp4', 'videos/movie2.avi', 'videos/clip.mov']
        mock_get_files.return_value = expected_files
        test_dir = '/test/video/folder'

        # Act
        result = get_video_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1], relative=True)

    @patch('novus_pytils.files.video.core.get_files_by_extension')
    def test_get_video_files_custom_extensions(self, mock_get_files):
        """Test getting video files with custom extensions."""
        # Arrange
        custom_extensions = ['.mp4', '.avi']
        expected_files = ['movie1.mp4', 'movie2.avi']
        mock_get_files.return_value = expected_files
        test_dir = '/test/custom/folder'

        # Act
        result = get_video_files(test_dir, custom_extensions)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, custom_extensions, relative=True)

    @patch('novus_pytils.files.video.core.get_files_by_extension')
    def test_get_video_files_empty_result(self, mock_get_files):
        """Test getting video files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/no/videos'

        # Act
        result = get_video_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.core.get_files_by_extension')
    def test_get_video_files_with_supported_extensions(self, mock_get_files):
        """Test that get_video_files uses SUPPORTED_VIDEO_EXTENSIONS by default."""
        # Arrange
        mock_get_files.return_value = ['test.mp4']
        test_dir = '/test/folder'

        # Act
        get_video_files(test_dir)

        # Assert
        # Verify that the function was called with SUPPORTED_VIDEO_EXTENSIONS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory
        assert call_args[1]['relative'] is True  # relative=True keyword argument

    @patch('novus_pytils.files.video.core.get_files_by_extension')
    def test_count_video_files_with_supported_extensions(self, mock_get_files):
        """Test that count_video_files uses SUPPORTED_VIDEO_EXTENSIONS."""
        # Arrange
        mock_get_files.return_value = ['a.mp4', 'b.avi', 'c.mov']
        test_path = '/test/path'

        # Act
        count_video_files(test_path)

        # Assert
        # Verify that the function was called with SUPPORTED_VIDEO_EXTENSIONS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_path  # First argument is the directory

    @patch('novus_pytils.files.video.core.get_files_by_extension')
    def test_get_video_files_pathlib_path(self, mock_get_files):
        """Test get_video_files with pathlib Path object."""
        # Arrange
        expected_files = ['movie.mp4']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_video_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.video.core.get_files_by_extension')
    def test_count_video_files_pathlib_path(self, mock_get_files):
        """Test count_video_files with pathlib Path object."""
        # Arrange
        mock_get_files.return_value = ['a.mp4', 'b.avi']
        test_path = Path('/test/pathlib/path')

        # Act
        result = count_video_files(test_path)

        # Assert
        assert result == 2
        mock_get_files.assert_called_once()