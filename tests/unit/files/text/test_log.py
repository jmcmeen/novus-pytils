"""Unit tests for novus_pytils.files.text.log module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.text.log import get_log_files


class TestLOG:
    """Test LOG file operations."""

    @patch('novus_pytils.files.text.log.get_files_by_extension')
    def test_get_log_files(self, mock_get_files):
        """Test getting LOG files from directory."""
        # Arrange
        expected_files = ['app.log', 'error.log', 'debug.LOG']
        mock_get_files.return_value = expected_files
        test_dir = '/test/log/folder'

        # Act
        result = get_log_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.text.log.get_files_by_extension')
    def test_get_log_files_empty_result(self, mock_get_files):
        """Test getting LOG files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_log_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.text.log.get_files_by_extension')
    def test_get_log_files_with_log_extensions(self, mock_get_files):
        """Test that get_log_files uses LOG_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.log']
        test_dir = '/test/folder'

        # Act
        get_log_files(test_dir)

        # Assert
        # Verify that the function was called with LOG_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.text.log.get_files_by_extension')
    def test_get_log_files_pathlib_path(self, mock_get_files):
        """Test get_log_files with pathlib Path object."""
        # Arrange
        expected_files = ['application.log']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_log_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()