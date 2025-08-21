"""Unit tests for file_operations.general module."""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests

from novus_pytils.directories import (
    download_file, get_files_by_extension, get_file_name,
    get_file_extension, get_file_size, file_exists, create_directory,
    copy_file, move_file, delete_file, delete_directory, get_directory_size,
    count_files_in_directory, get_subdirectories, create_file_from_content,
    read_file_content, append_to_file, get_file_creation_time,
    get_file_modification_time, is_file_empty, get_files_recursively,
    filter_files_by_size, filter_files_by_date, rename_file,
    get_file_permissions, set_file_permissions, create_backup,
    restore_backup, sync_directories
)


class TestDownloadFile:
    """Test download_file function."""
    
    @patch('novus_pytils.directories.requests.get')
    def test_download_file_success(self, mock_get, temp_dir):
        """Test successful file download."""
        mock_response = MagicMock()
        mock_response.content = b"test content"
        mock_get.return_value = mock_response
        
        save_path = temp_dir / "downloaded_file.txt"
        download_file("http://example.com/file.txt", str(save_path))
        
        assert save_path.exists()
        assert save_path.read_bytes() == b"test content"
        mock_get.assert_called_once_with("http://example.com/file.txt")
    
    @patch('novus_pytils.directories.requests.get')
    def test_download_file_http_error(self, mock_get, temp_dir):
        """Test download with HTTP error."""
        mock_get.side_effect = requests.RequestException("Connection error")
        
        save_path = temp_dir / "downloaded_file.txt"
        with pytest.raises(requests.RequestException):
            download_file("http://example.com/file.txt", str(save_path))

class TestFileQueries:
    """Test file query functions."""
    
    def test_get_files_by_extension(self, temp_dir):
        """Test getting files by extension."""
        # Create test files
        (temp_dir / "file1.txt").touch()
        (temp_dir / "file2.txt").touch()
        (temp_dir / "file3.py").touch()
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file4.txt").touch()
        
        txt_files = get_files_by_extension(str(temp_dir), ['.txt'])
        assert len(txt_files) == 2
        assert all(f.endswith('.txt') for f in txt_files)
        
        # Test recursive
        txt_files_recursive = get_files_by_extension(str(temp_dir), ['.txt'], recursive=True)
        assert len(txt_files_recursive) == 3
    
    def test_get_file_name(self, sample_text_file):
        """Test getting file name."""
        assert get_file_name(str(sample_text_file)) == "sample"
    
    def test_get_file_extension(self, sample_text_file):
        """Test getting file extension."""
        assert get_file_extension(str(sample_text_file)) == ".txt"
    
    def test_get_file_size(self, sample_text_file):
        """Test getting file size."""
        size = get_file_size(str(sample_text_file))
        assert size > 0
        assert isinstance(size, int)
    
    def test_file_exists(self, sample_text_file, temp_dir):
        """Test file existence check."""
        assert file_exists(str(sample_text_file)) is True
        assert file_exists(str(temp_dir / "nonexistent.txt")) is False


class TestDirectoryOperations:
    """Test directory operations."""
    
    def test_create_directory(self, temp_dir):
        """Test directory creation."""
        new_dir = temp_dir / "new_directory"
        create_directory(str(new_dir))
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_create_directory_nested(self, temp_dir):
        """Test nested directory creation."""
        nested_dir = temp_dir / "level1" / "level2" / "level3"
        create_directory(str(nested_dir))
        assert nested_dir.exists()
        assert nested_dir.is_dir()
    
    def test_get_subdirectories(self, temp_dir):
        """Test getting subdirectories."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir2").mkdir()
        (temp_dir / "file.txt").touch()
        
        subdirs = get_subdirectories(str(temp_dir))
        assert len(subdirs) == 2
        assert all(Path(d).name in ['dir1', 'dir2'] for d in subdirs)
    
    def test_get_directory_size(self, temp_dir):
        """Test getting directory size."""
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        
        size = get_directory_size(str(temp_dir))
        assert size > 0
        assert isinstance(size, int)
    
    def test_count_files_in_directory(self, temp_dir):
        """Test counting files in directory."""
        (temp_dir / "file1.txt").touch()
        (temp_dir / "file2.txt").touch()
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file3.txt").touch()
        
        count = count_files_in_directory(str(temp_dir))
        assert count == 2  # Only files in root directory
        
        count_recursive = count_files_in_directory(str(temp_dir), recursive=True)
        assert count_recursive == 3  # All files including subdirectories


class TestFileOperations:
    """Test file operations."""
    
    def test_copy_file(self, sample_text_file, temp_dir):
        """Test file copying."""
        dest_path = temp_dir / "copied_file.txt"
        copy_file(str(sample_text_file), str(dest_path))
        
        assert dest_path.exists()
        assert dest_path.read_text() == sample_text_file.read_text()
    
    def test_move_file(self, temp_dir):
        """Test file moving."""
        source_path = temp_dir / "source.txt"
        source_path.write_text("test content")
        dest_path = temp_dir / "destination.txt"
        
        move_file(str(source_path), str(dest_path))
        
        assert not source_path.exists()
        assert dest_path.exists()
        assert dest_path.read_text() == "test content"
    
    def test_delete_file(self, sample_text_file):
        """Test file deletion."""
        assert sample_text_file.exists()
        delete_file(str(sample_text_file))
        assert not sample_text_file.exists()
    
    def test_delete_directory(self, temp_dir):
        """Test directory deletion."""
        test_dir = temp_dir / "test_directory"
        test_dir.mkdir()
        (test_dir / "file.txt").touch()
        
        delete_directory(str(test_dir))
        assert not test_dir.exists()
    
    def test_rename_file(self, temp_dir):
        """Test file renaming."""
        original_path = temp_dir / "original.txt"
        original_path.write_text("content")
        new_path = temp_dir / "renamed.txt"
        
        rename_file(str(original_path), str(new_path))
        
        assert not original_path.exists()
        assert new_path.exists()
        assert new_path.read_text() == "content"


class TestFileContent:
    """Test file content operations."""
    
    def test_create_file_from_content(self, temp_dir):
        """Test creating file from content."""
        file_path = temp_dir / "new_file.txt"
        content = "This is new content"
        
        create_file_from_content(str(file_path), content)
        
        assert file_path.exists()
        assert file_path.read_text() == content
    
    def test_read_file_content(self, sample_text_file):
        """Test reading file content."""
        content = read_file_content(str(sample_text_file))
        assert "sample text file" in content
    
    def test_append_to_file(self, sample_text_file):
        """Test appending to file."""
        original_content = sample_text_file.read_text()
        append_content = "\nAppended line"
        
        append_to_file(str(sample_text_file), append_content)
        
        new_content = sample_text_file.read_text()
        assert new_content == original_content + append_content
    
    def test_is_file_empty(self, temp_dir):
        """Test checking if file is empty."""
        empty_file = temp_dir / "empty.txt"
        empty_file.touch()
        non_empty_file = temp_dir / "non_empty.txt"
        non_empty_file.write_text("content")
        
        assert is_file_empty(str(empty_file)) is True
        assert is_file_empty(str(non_empty_file)) is False


class TestFileFiltering:
    """Test file filtering functions."""
    
    def test_get_files_recursively(self, mock_file_structure):
        """Test getting files recursively."""
        files = get_files_recursively(str(mock_file_structure))
        assert len(files) >= 5  # Should find all files in structure
        
        # Test with extension filter
        txt_files = get_files_recursively(str(mock_file_structure), extensions=['.txt'])
        assert all(f.endswith('.txt') for f in txt_files)
    
    def test_filter_files_by_size(self, temp_dir):
        """Test filtering files by size."""
        small_file = temp_dir / "small.txt"
        large_file = temp_dir / "large.txt"
        
        small_file.write_text("small")
        large_file.write_text("large content with more text")
        
        files = [str(small_file), str(large_file)]
        
        # Filter files larger than 10 bytes
        large_files = filter_files_by_size(files, min_size=10)
        assert str(large_file) in large_files
        assert str(small_file) not in large_files
    
    def test_filter_files_by_date(self, temp_dir):
        """Test filtering files by date."""
        import time
        
        old_file = temp_dir / "old.txt"
        old_file.write_text("old content")
        
        time.sleep(0.1)  # Small delay
        
        new_file = temp_dir / "new.txt"
        new_file.write_text("new content")
        
        files = [str(old_file), str(new_file)]
        
        # Filter files modified in the last 1 second
        import datetime
        cutoff_time = datetime.datetime.now() - datetime.timedelta(seconds=1)
        recent_files = filter_files_by_date(files, after=cutoff_time)
        
        assert len(recent_files) == 2  # Both should be recent


class TestFileMetadata:
    """Test file metadata functions."""
    
    def test_get_file_creation_time(self, sample_text_file):
        """Test getting file creation time."""
        creation_time = get_file_creation_time(str(sample_text_file))
        assert creation_time is not None
        assert isinstance(creation_time, float)
    
    def test_get_file_modification_time(self, sample_text_file):
        """Test getting file modification time."""
        mod_time = get_file_modification_time(str(sample_text_file))
        assert mod_time is not None
        assert isinstance(mod_time, float)
    
    @pytest.mark.skipif(os.name == 'nt', reason="Permissions work differently on Windows")
    def test_file_permissions(self, sample_text_file):
        """Test getting and setting file permissions."""
        original_perms = get_file_permissions(str(sample_text_file))
        assert original_perms is not None
        
        # Set new permissions (readable only)
        set_file_permissions(str(sample_text_file), 0o444)
        new_perms = get_file_permissions(str(sample_text_file))
        assert new_perms != original_perms


class TestBackupOperations:
    """Test backup and restore operations."""
    
    def test_create_backup(self, sample_text_file, temp_dir):
        """Test creating file backup."""
        backup_path = create_backup(str(sample_text_file), str(temp_dir))
        
        assert os.path.exists(backup_path)
        assert Path(backup_path).read_text() == sample_text_file.read_text()
    
    def test_restore_backup(self, temp_dir):
        """Test restoring from backup."""
        original_file = temp_dir / "original.txt"
        original_content = "original content"
        original_file.write_text(original_content)
        
        # Create backup
        backup_path = create_backup(str(original_file), str(temp_dir))
        
        # Modify original
        original_file.write_text("modified content")
        
        # Restore from backup
        restore_backup(backup_path, str(original_file))
        
        assert original_file.read_text() == original_content


class TestDirectorySync:
    """Test directory synchronization."""
    
    def test_sync_directories(self, temp_dir):
        """Test directory synchronization."""
        source_dir = temp_dir / "source"
        dest_dir = temp_dir / "destination"
        
        source_dir.mkdir()
        dest_dir.mkdir()
        
        # Create files in source
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")
        
        sync_directories(str(source_dir), str(dest_dir))
        
        assert (dest_dir / "file1.txt").exists()
        assert (dest_dir / "file2.txt").exists()
        assert (dest_dir / "file1.txt").read_text() == "content1"