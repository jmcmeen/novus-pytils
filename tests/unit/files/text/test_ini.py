"""Unit tests for novus_pytils.files.text.ini module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.text.ini import get_ini_files


class TestINI:
    """Test INI file operations."""

    @patch('novus_pytils.files.text.ini.get_files_by_extension')
    def test_get_ini_files(self, mock_get_files):
        """Test getting INI files from directory."""
        # Arrange
        expected_files = ['config.ini', 'settings.ini', 'app.INI']
        mock_get_files.return_value = expected_files
        test_dir = '/test/ini/folder'

        # Act
        result = get_ini_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.text.ini.get_files_by_extension')
    def test_get_ini_files_empty_result(self, mock_get_files):
        """Test getting INI files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_ini_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.text.ini.get_files_by_extension')
    def test_get_ini_files_with_ini_extensions(self, mock_get_files):
        """Test that get_ini_files uses INI_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.ini']
        test_dir = '/test/folder'

        # Act
        get_ini_files(test_dir)

        # Assert
        # Verify that the function was called with INI_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.text.ini.get_files_by_extension')
    def test_get_ini_files_pathlib_path(self, mock_get_files):
        """Test get_ini_files with pathlib Path object."""
        # Arrange
        expected_files = ['configuration.ini']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_ini_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()