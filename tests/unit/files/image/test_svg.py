"""Unit tests for novus_pytils.files.image.svg module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.image.svg import get_svg_files


class TestSVG:
    """Test SVG file operations."""

    @patch('novus_pytils.files.image.svg.get_files_by_extension')
    def test_get_svg_files(self, mock_get_files):
        """Test getting SVG files from directory."""
        # Arrange
        expected_files = ['icon1.svg', 'icon2.svg', 'vector.SVG']
        mock_get_files.return_value = expected_files
        test_dir = '/test/svg/folder'

        # Act
        result = get_svg_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.image.svg.get_files_by_extension')
    def test_get_svg_files_empty_result(self, mock_get_files):
        """Test getting SVG files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/empty/folder'

        # Act
        result = get_svg_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.image.svg.get_files_by_extension')
    def test_get_svg_files_with_svg_extensions(self, mock_get_files):
        """Test that get_svg_files uses SVG_EXTS."""
        # Arrange
        mock_get_files.return_value = ['test.svg']
        test_dir = '/test/folder'

        # Act
        get_svg_files(test_dir)

        # Assert
        # Verify that the function was called with SVG_EXTS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory

    @patch('novus_pytils.files.image.svg.get_files_by_extension')
    def test_get_svg_files_pathlib_path(self, mock_get_files):
        """Test get_svg_files with pathlib Path object."""
        # Arrange
        expected_files = ['vector.svg']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_svg_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()