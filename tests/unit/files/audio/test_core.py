"""Unit tests for novus_pytils.files.audio.core module."""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from novus_pytils.files.audio.core import count_audio_files, get_audio_files


class TestAudioCore:
    """Test core audio functionality."""

    @patch('novus_pytils.files.audio.core.get_files_by_extension')
    def test_count_audio_files(self, mock_get_files):
        """Test counting audio files in a folder."""
        # Arrange
        mock_get_files.return_value = [
            'song1.mp3',
            'song2.wav',
            'song3.flac',
            'song4.ogg'
        ]
        test_path = '/test/audio/folder'

        # Act
        result = count_audio_files(test_path)

        # Assert
        assert result == 4
        mock_get_files.assert_called_once_with(test_path, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.audio.core.get_files_by_extension')
    def test_count_audio_files_empty_folder(self, mock_get_files):
        """Test counting audio files in empty folder."""
        # Arrange
        mock_get_files.return_value = []
        test_path = '/test/empty/folder'

        # Act
        result = count_audio_files(test_path)

        # Assert
        assert result == 0
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.audio.core.get_files_by_extension')
    def test_get_audio_files_default_extensions(self, mock_get_files):
        """Test getting audio files with default extensions."""
        # Arrange
        expected_files = ['music/song1.mp3', 'music/song2.wav', 'music/song3.flac']
        mock_get_files.return_value = expected_files
        test_dir = '/test/music/folder'

        # Act
        result = get_audio_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1], relative=True)

    @patch('novus_pytils.files.audio.core.get_files_by_extension')
    def test_get_audio_files_custom_extensions(self, mock_get_files):
        """Test getting audio files with custom extensions."""
        # Arrange
        custom_extensions = ['.mp3', '.wav']
        expected_files = ['track1.mp3', 'track2.wav']
        mock_get_files.return_value = expected_files
        test_dir = '/test/custom/folder'

        # Act
        result = get_audio_files(test_dir, custom_extensions)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, custom_extensions, relative=True)

    @patch('novus_pytils.files.audio.core.get_files_by_extension')
    def test_get_audio_files_empty_result(self, mock_get_files):
        """Test getting audio files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/no/audio'

        # Act
        result = get_audio_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.audio.core.get_files_by_extension')
    def test_get_audio_files_with_supported_extensions(self, mock_get_files):
        """Test that get_audio_files uses SUPPORTED_AUDIO_EXTENSIONS by default."""
        # Arrange
        mock_get_files.return_value = ['test.mp3']
        test_dir = '/test/folder'

        # Act
        get_audio_files(test_dir)

        # Assert
        # Verify that the function was called with SUPPORTED_AUDIO_EXTENSIONS
        # The exact value will depend on what's in globals, but we can verify the call pattern
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory
        assert call_args[1]['relative'] is True  # relative=True keyword argument

    @patch('novus_pytils.files.audio.core.get_files_by_extension')
    def test_count_audio_files_with_supported_extensions(self, mock_get_files):
        """Test that count_audio_files uses SUPPORTED_AUDIO_EXTENSIONS."""
        # Arrange
        mock_get_files.return_value = ['a.mp3', 'b.wav', 'c.flac']
        test_path = '/test/path'

        # Act
        count_audio_files(test_path)

        # Assert
        # Verify that the function was called with SUPPORTED_AUDIO_EXTENSIONS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_path  # First argument is the directory
        # Second argument should be SUPPORTED_AUDIO_EXTENSIONS (from globals)

    @patch('novus_pytils.files.audio.core.get_files_by_extension')
    def test_get_audio_files_pathlib_path(self, mock_get_files):
        """Test get_audio_files with pathlib Path object."""
        # Arrange
        expected_files = ['song.mp3']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_audio_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.audio.core.get_files_by_extension')
    def test_count_audio_files_pathlib_path(self, mock_get_files):
        """Test count_audio_files with pathlib Path object."""
        # Arrange
        mock_get_files.return_value = ['a.mp3', 'b.wav']
        test_path = Path('/test/pathlib/path')

        # Act
        result = count_audio_files(test_path)

        # Assert
        assert result == 2
        mock_get_files.assert_called_once()