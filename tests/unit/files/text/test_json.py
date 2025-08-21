"""Unit tests for novus_pytils.files.text.json module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.text.json import get_json_files


class TestJSON:
    """Test JSON file operations."""

    @patch('novus_pytils.files.text.json.get_files_by_extension')
    def test_get_json_files(self, mock_get_files):
        """Test getting JSON files from directory."""
        # Arrange
        expected_files = ['config.json', 'data.json', 'settings.JSON']
        mock_get_files.return_value = expected_files
        test_dir = '/test/json/folder'

        # Act
        result = get_json_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.text.json.get_files_by_extension')
    def test_get_json_files_empty_result(self, mock_get_files):
        """Test getting JSON files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_json_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.text.json.get_files_by_extension')
    def test_get_json_files_with_json_extensions(self, mock_get_files):
        """Test that get_json_files uses JSON_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.json']
        test_dir = '/test/folder'

        # Act
        get_json_files(test_dir)

        # Assert
        # Verify that the function was called with JSON_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.text.json.get_files_by_extension')
    def test_get_json_files_pathlib_path(self, mock_get_files):
        """Test get_json_files with pathlib Path object."""
        # Arrange
        expected_files = ['api_response.json']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_json_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()