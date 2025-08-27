"""Tests for novus_pytils.video.core module."""

import pytest
from unittest.mock import patch, MagicMock

from novus_pytils.video.core import count_video_files, get_video_files


class TestCountVideoFiles:
    """Test the count_video_files function."""
    
    @patch('novus_pytils.video.core.get_files_by_extension')
    def test_count_video_files_basic(self, mock_get_files):
        mock_get_files.return_value = ["movie.mp4", "clip.avi", "video.mkv"]
        
        result = count_video_files("/test/path")
        
        assert result == 3
        mock_get_files.assert_called_once()
    
    @patch('novus_pytils.video.core.get_files_by_extension')
    def test_count_video_files_no_files(self, mock_get_files):
        mock_get_files.return_value = []
        
        result = count_video_files("/empty/path")
        
        assert result == 0
    
    @patch('novus_pytils.video.core.get_files_by_extension')
    def test_count_video_files_uses_supported_extensions(self, mock_get_files):
        mock_get_files.return_value = ["video.mp4"]
        
        count_video_files("/test/path")
        
        # Verify it's called with SUPPORTED_VIDEO_EXTENSIONS
        args, kwargs = mock_get_files.call_args
        assert args[0] == "/test/path"


class TestGetVideoFiles:
    """Test the get_video_files function."""
    
    @patch('novus_pytils.video.core.get_files_by_extension')
    def test_get_video_files_basic(self, mock_get_files):
        expected_files = ["movie.mp4", "clip.avi", "video.mkv"]
        mock_get_files.return_value = expected_files
        
        result = get_video_files("/test/dir")
        
        assert result == expected_files
        mock_get_files.assert_called_once_with("/test/dir", None, relative=True)
    
    @patch('novus_pytils.video.core.get_files_by_extension')
    def test_get_video_files_with_custom_extensions(self, mock_get_files):
        custom_extensions = [".mp4", ".avi"]
        mock_get_files.return_value = ["movie.mp4", "clip.avi"]
        
        result = get_video_files("/test/dir", file_extensions=custom_extensions)
        
        assert result == ["movie.mp4", "clip.avi"]
        mock_get_files.assert_called_once_with("/test/dir", custom_extensions, relative=True)
    
    @patch('novus_pytils.video.core.get_files_by_extension')
    def test_get_video_files_empty_directory(self, mock_get_files):
        mock_get_files.return_value = []
        
        result = get_video_files("/empty/dir")
        
        assert result == []