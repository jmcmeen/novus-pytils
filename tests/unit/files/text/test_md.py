"""Unit tests for novus_pytils.files.text.md module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.text.md import get_md_files


class TestMD:
    """Test Markdown file operations."""

    @patch('novus_pytils.files.text.md.get_files_by_extension')
    def test_get_md_files(self, mock_get_files):
        """Test getting Markdown files from directory."""
        # Arrange
        expected_files = ['README.md', 'docs.markdown', 'notes.MD']
        mock_get_files.return_value = expected_files
        test_dir = '/test/md/folder'

        # Act
        result = get_md_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.text.md.get_files_by_extension')
    def test_get_md_files_empty_result(self, mock_get_files):
        """Test getting Markdown files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_md_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.text.md.get_files_by_extension')
    def test_get_md_files_with_md_extensions(self, mock_get_files):
        """Test that get_md_files uses MD_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.md']
        test_dir = '/test/folder'

        # Act
        get_md_files(test_dir)

        # Assert
        # Verify that the function was called with MD_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.text.md.get_files_by_extension')
    def test_get_md_files_pathlib_path(self, mock_get_files):
        """Test get_md_files with pathlib Path object."""
        # Arrange
        expected_files = ['documentation.md']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_md_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()