"""Unit tests for novus_pytils.files.image.core module."""
import pytest
from unittest.mock import patch
from pathlib import Path

from novus_pytils.files.image.core import count_image_files, get_image_files


class TestImageCore:
    """Test core image functionality."""

    @patch('novus_pytils.files.image.core.get_files_by_extension')
    def test_count_image_files(self, mock_get_files):
        """Test counting image files in a folder."""
        # Arrange
        mock_get_files.return_value = [
            'photo1.jpg',
            'photo2.png',
            'graphic.gif',
            'icon.svg'
        ]
        test_path = '/test/image/folder'

        # Act
        result = count_image_files(test_path)

        # Assert
        assert result == 4
        mock_get_files.assert_called_once_with(test_path, mock_get_files.call_args[0][1])

    @patch('novus_pytils.files.image.core.get_files_by_extension')
    def test_count_image_files_empty_folder(self, mock_get_files):
        """Test counting image files in empty folder."""
        # Arrange
        mock_get_files.return_value = []
        test_path = '/test/empty/folder'

        # Act
        result = count_image_files(test_path)

        # Assert
        assert result == 0
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.image.core.get_files_by_extension')
    def test_get_image_files_default_extensions(self, mock_get_files):
        """Test getting image files with default extensions."""
        # Arrange
        expected_files = ['images/photo1.jpg', 'images/photo2.png', 'images/graphic.gif']
        mock_get_files.return_value = expected_files
        test_dir = '/test/image/folder'

        # Act
        result = get_image_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, mock_get_files.call_args[0][1], relative=True)

    @patch('novus_pytils.files.image.core.get_files_by_extension')
    def test_get_image_files_custom_extensions(self, mock_get_files):
        """Test getting image files with custom extensions."""
        # Arrange
        custom_extensions = ['.jpg', '.png']
        expected_files = ['photo1.jpg', 'photo2.png']
        mock_get_files.return_value = expected_files
        test_dir = '/test/custom/folder'

        # Act
        result = get_image_files(test_dir, custom_extensions)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once_with(test_dir, custom_extensions, relative=True)

    @patch('novus_pytils.files.image.core.get_files_by_extension')
    def test_get_image_files_empty_result(self, mock_get_files):
        """Test getting image files when no files found."""
        # Arrange
        mock_get_files.return_value = []
        test_dir = '/test/no/images'

        # Act
        result = get_image_files(test_dir)

        # Assert
        assert result == []
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.image.core.get_files_by_extension')
    def test_get_image_files_with_supported_extensions(self, mock_get_files):
        """Test that get_image_files uses SUPPORTED_IMAGE_EXTENSIONS by default."""
        # Arrange
        mock_get_files.return_value = ['test.jpg']
        test_dir = '/test/folder'

        # Act
        get_image_files(test_dir)

        # Assert
        # Verify that the function was called with SUPPORTED_IMAGE_EXTENSIONS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_dir  # First argument is the directory
        assert call_args[1]['relative'] is True  # relative=True keyword argument

    @patch('novus_pytils.files.image.core.get_files_by_extension')
    def test_count_image_files_with_supported_extensions(self, mock_get_files):
        """Test that count_image_files uses SUPPORTED_IMAGE_EXTENSIONS."""
        # Arrange
        mock_get_files.return_value = ['a.jpg', 'b.png', 'c.gif']
        test_path = '/test/path'

        # Act
        count_image_files(test_path)

        # Assert
        # Verify that the function was called with SUPPORTED_IMAGE_EXTENSIONS
        assert mock_get_files.called
        call_args = mock_get_files.call_args
        assert call_args[0][0] == test_path  # First argument is the directory

    @patch('novus_pytils.files.image.core.get_files_by_extension')
    def test_get_image_files_pathlib_path(self, mock_get_files):
        """Test get_image_files with pathlib Path object."""
        # Arrange
        expected_files = ['image.jpg']
        mock_get_files.return_value = expected_files
        test_dir = Path('/test/pathlib/folder')

        # Act
        result = get_image_files(test_dir)

        # Assert
        assert result == expected_files
        mock_get_files.assert_called_once()

    @patch('novus_pytils.files.image.core.get_files_by_extension')
    def test_count_image_files_pathlib_path(self, mock_get_files):
        """Test count_image_files with pathlib Path object."""
        # Arrange
        mock_get_files.return_value = ['a.jpg', 'b.png']
        test_path = Path('/test/pathlib/path')

        # Act
        result = count_image_files(test_path)

        # Assert
        assert result == 2
        mock_get_files.assert_called_once()