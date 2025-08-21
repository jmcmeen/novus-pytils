from novus_pytils.zip import (
    get_zip_files, extract_zip_file, create_zip_file, list_zip_contents, get_zip_info,
    extract_single_file, is_valid_zip, zip_directory, add_files_to_zip,
    remove_files_from_zip, extract_files_by_pattern, add_directory_to_zip, ZipFile
)
import pytest
import zipfile
import os


class TestGetZipFiles:
    """Test get_zip_files function."""
    
    def test_get_zip_files_with_zip_files(self, temp_dir):
        """Test getting zip files from directory with zip files."""
        # Create test zip files
        (temp_dir / "test1.zip").touch()
        (temp_dir / "test2.zip").touch()
        (temp_dir / "archive.7z").touch()
        (temp_dir / "document.txt").touch()
        
        zip_files = get_zip_files(str(temp_dir))
        
        # Should find only .zip files (based on ZIP_EXTENSIONS)
        zip_paths = [os.path.basename(path) for path in zip_files]
        assert "test1.zip" in zip_paths
        assert "test2.zip" in zip_paths
        assert "archive.7z" not in zip_paths  # .7z is not in ZIP_EXTENSIONS
        assert "document.txt" not in zip_paths
    
    def test_get_zip_files_empty_directory(self, temp_dir):
        """Test getting zip files from empty directory."""
        zip_files = get_zip_files(str(temp_dir))
        assert zip_files == []
    
    def test_get_zip_files_no_zip_files(self, temp_dir):
        """Test getting zip files from directory with no zip files."""
        (temp_dir / "document.txt").touch()
        (temp_dir / "image.jpg").touch()
        
        zip_files = get_zip_files(str(temp_dir))
        assert zip_files == []


class TestAddDirectoryToZip:
    """Test add_directory_to_zip function."""
    
    def test_add_directory_to_zip_with_archive_dir(self, temp_dir):
        """Test adding directory to zip with custom archive directory name."""
        # Create test directory structure
        test_dir = temp_dir / "source_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "subdir").mkdir()
        (test_dir / "subdir" / "file2.txt").write_text("content2")
        
        # Create zip and add directory
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zip_ref:
            add_directory_to_zip(zip_ref, str(test_dir), "custom_name")
        
        # Verify contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "custom_name/file1.txt" in names
            assert "custom_name/subdir/file2.txt" in names
    
    def test_add_directory_to_zip_without_archive_dir(self, temp_dir):
        """Test adding directory to zip without archive directory name."""
        # Create test directory structure
        test_dir = temp_dir / "source_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "subdir").mkdir()
        (test_dir / "subdir" / "file2.txt").write_text("content2")
        
        # Create zip and add directory
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zip_ref:
            add_directory_to_zip(zip_ref, str(test_dir), "")
        
        # Verify contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "file1.txt" in names
            assert "subdir/file2.txt" in names


class TestExtractZip:
    """Test extract_zip function."""
    
    def test_extract_zip_success(self, temp_dir):
        """Test successful ZIP extraction."""
        # Create a test zip file
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("dir/file2.txt", "content2")
        
        extract_dir = temp_dir / "extracted"
        extract_zip_file(str(zip_path), str(extract_dir))
        
        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "dir" / "file2.txt").exists()
        assert (extract_dir / "file1.txt").read_text() == "content1"
    
    def test_extract_zip_nonexistent_file(self, temp_dir):
        """Test extraction of non-existent ZIP file."""
        with pytest.raises(FileNotFoundError):
            extract_zip_file(str(temp_dir / "nonexistent.zip"), str(temp_dir))


class TestCreateZip:
    """Test create_zip_file function."""
    
    def test_create_zip_with_file_list(self, temp_dir):
        """Test creating ZIP with list of files."""
        # Create test files
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        
        zip_path = temp_dir / "test.zip"
        create_zip_file(str(zip_path), [str(file1), str(file2)])
        
        assert zip_path.exists()
        
        # Verify contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "file1.txt" in names
            assert "file2.txt" in names
    
    def test_create_zip_with_dict_mapping(self, temp_dir):
        """Test creating ZIP with dictionary mapping."""
        # Create test file
        file1 = temp_dir / "file1.txt"
        file1.write_text("content1")
        
        zip_path = temp_dir / "test.zip"
        files_dict = {str(file1): "renamed_file.txt"}
        create_zip_file(str(zip_path), files_dict)
        
        assert zip_path.exists()
        
        # Verify contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "renamed_file.txt" in names
            assert zf.read("renamed_file.txt").decode() == "content1"
    
    def test_create_zip_with_directory(self, temp_dir):
        """Test creating ZIP with directory."""
        # Create test directory structure
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "subdir").mkdir()
        (test_dir / "subdir" / "file2.txt").write_text("content2")
        
        zip_path = temp_dir / "test.zip"
        create_zip_file(str(zip_path), [str(test_dir)])
        
        assert zip_path.exists()
        
        # Verify contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert any("file1.txt" in name for name in names)
            assert any("file2.txt" in name for name in names)


class TestListZipContents:
    """Test list_zip_contents function."""
    
    def test_list_zip_contents(self, temp_dir):
        """Test listing ZIP contents."""
        # Create test zip
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("dir/file2.txt", "content2")
        
        contents = list_zip_contents(str(zip_path))
        
        assert "file1.txt" in contents
        assert "dir/file2.txt" in contents
        assert len(contents) == 2


class TestGetZipInfo:
    """Test get_zip_info function."""
    
    def test_get_zip_info(self, temp_dir):
        """Test getting ZIP information."""
        # Create test zip
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "longer content for testing compression")
        
        info = get_zip_info(str(zip_path))
        
        assert info['filename'] == "test.zip"
        assert info['file_count'] == 2
        assert info['total_size'] > 0
        assert info['compressed_size'] >= 0
        assert 'compression_ratio' in info
        assert "file1.txt" in info['files']
        assert "file2.txt" in info['files']
        assert len(info['file_details']) == 2


class TestExtractSingleFile:
    """Test extract_single_file function."""
    
    def test_extract_single_file_success(self, temp_dir):
        """Test extracting a single file."""
        # Create test zip
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
        
        extract_dir = temp_dir / "extracted"
        result_path = extract_single_file(str(zip_path), "file1.txt", str(extract_dir))
        
        assert os.path.exists(result_path)
        assert (extract_dir / "file1.txt").read_text() == "content1"
        assert not (extract_dir / "file2.txt").exists()
    
    def test_extract_single_file_not_found(self, temp_dir):
        """Test extracting non-existent file."""
        # Create test zip
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
        
        extract_dir = temp_dir / "extracted"
        with pytest.raises(KeyError):
            extract_single_file(str(zip_path), "nonexistent.txt", str(extract_dir))


class TestIsValidZip:
    """Test is_valid_zip function."""
    
    def test_is_valid_zip_true(self, temp_dir):
        """Test with valid ZIP file."""
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
        
        assert is_valid_zip(str(zip_path)) is True
    
    def test_is_valid_zip_false_invalid_file(self, temp_dir):
        """Test with invalid ZIP file."""
        invalid_file = temp_dir / "invalid.zip"
        invalid_file.write_text("This is not a ZIP file")
        
        assert is_valid_zip(str(invalid_file)) is False
    
    def test_is_valid_zip_false_nonexistent_file(self, temp_dir):
        """Test with non-existent file."""
        assert is_valid_zip(str(temp_dir / "nonexistent.zip")) is False


class TestZipDirectory:
    """Test zip_directory function."""
    
    def test_zip_directory_without_root(self, temp_dir):
        """Test zipping directory without including root."""
        # Create test directory
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "subdir").mkdir()
        (test_dir / "subdir" / "file2.txt").write_text("content2")
        
        zip_path = temp_dir / "test.zip"
        zip_directory(str(test_dir), str(zip_path), include_root=False)
        
        assert zip_path.exists()
        
        # Verify contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "file1.txt" in names
            assert "subdir/file2.txt" in names
    
    def test_zip_directory_with_root(self, temp_dir):
        """Test zipping directory including root."""
        # Create test directory
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        
        zip_path = temp_dir / "test.zip"
        zip_directory(str(test_dir), str(zip_path), include_root=True)
        
        assert zip_path.exists()
        
        # Verify contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert any("test_dir" in name for name in names)


class TestAddFilesToZip:
    """Test add_files_to_zip function."""
    
    def test_add_files_to_existing_zip(self, temp_dir):
        """Test adding files to existing ZIP."""
        # Create initial ZIP
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("existing.txt", "existing content")
        
        # Create new file to add
        new_file = temp_dir / "new_file.txt"
        new_file.write_text("new content")
        
        add_files_to_zip(str(zip_path), [str(new_file)])
        
        # Verify both files exist
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "existing.txt" in names
            assert "new_file.txt" in names
            assert zf.read("existing.txt").decode() == "existing content"
            assert zf.read("new_file.txt").decode() == "new content"


class TestRemoveFilesFromZip:
    """Test remove_files_from_zip function."""
    
    def test_remove_files_from_zip(self, temp_dir):
        """Test removing files from ZIP."""
        # Create ZIP with multiple files
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
            zf.writestr("file3.txt", "content3")
        
        remove_files_from_zip(str(zip_path), ["file2.txt"])
        
        # Verify file was removed
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "file1.txt" in names
            assert "file2.txt" not in names
            assert "file3.txt" in names


class TestExtractFilesByPattern:
    """Test extract_files_by_pattern function."""
    
    def test_extract_files_by_pattern(self, temp_dir):
        """Test extracting files by pattern."""
        # Create ZIP with various files
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("data1.txt", "content1")
            zf.writestr("data2.txt", "content2")
            zf.writestr("readme.md", "readme content")
            zf.writestr("config.json", "config content")
        
        extract_dir = temp_dir / "extracted"
        extracted_files = extract_files_by_pattern(str(zip_path), "*.txt", str(extract_dir))
        
        assert len(extracted_files) == 2
        assert (extract_dir / "data1.txt").exists()
        assert (extract_dir / "data2.txt").exists()
        assert not (extract_dir / "readme.md").exists()
        assert not (extract_dir / "config.json").exists()


class TestZipFile:
    """Test ZipFile context manager."""
    
    def test_zip_file_create(self, temp_dir):
        """Test creating ZIP with ZipFile."""
        zip_path = temp_dir / "test.zip"
        
        zip_file = ZipFile(str(zip_path), 'w')
        with zip_file as zf:
            zip_file.add_string("content1", "file1.txt")
            zip_file.add_string("content2", "file2.txt")
        
        assert zip_path.exists()
        
        # Verify contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            assert zf.read("file1.txt").decode() == "content1"
            assert zf.read("file2.txt").decode() == "content2"
    
    def test_zip_file_read(self, temp_dir):
        """Test reading ZIP with ZipFile."""
        # Create test ZIP
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
        
        zip_file = ZipFile(str(zip_path), 'r')
        with zip_file as zf:
            files = zip_file.list_files()
            assert "file1.txt" in files
            assert "file2.txt" in files
    
    def test_zip_file_add_file(self, temp_dir):
        """Test adding physical file with ZipFile."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        zip_path = temp_dir / "test.zip"
        
        zip_file = ZipFile(str(zip_path), 'w')
        with zip_file as zf:
            zip_file.add_file(str(test_file))
            zip_file.add_file(str(test_file), "renamed.txt")
        
        # Verify contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "test.txt" in names
            assert "renamed.txt" in names
            assert zf.read("test.txt").decode() == "test content"
            assert zf.read("renamed.txt").decode() == "test content"
    
    def test_zip_file_extract_all(self, temp_dir):
        """Test extracting all files with ZipFile."""
        # Create test ZIP
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("dir/file2.txt", "content2")
        
        extract_dir = temp_dir / "extracted"
        
        zip_file = ZipFile(str(zip_path), 'r')
        with zip_file as zf:
            zip_file.extract_all(str(extract_dir))
        
        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "dir" / "file2.txt").exists()


class TestZipUtilsIntegration:
    """Integration tests for ZIP utilities."""
    
    def test_full_workflow(self, temp_dir):
        """Test complete workflow: create, modify, extract."""
        # Create test files
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        
        zip_path = temp_dir / "workflow.zip"
        
        # 1. Create ZIP
        create_zip_file(str(zip_path), [str(file1), str(file2)])
        
        # 2. Verify it's valid
        assert is_valid_zip(str(zip_path))
        
        # 3. Check contents
        contents = list_zip_contents(str(zip_path))
        assert len(contents) == 2
        
        # 4. Get info
        info = get_zip_info(str(zip_path))
        assert info['file_count'] == 2
        
        # 5. Add another file
        file3 = temp_dir / "file3.txt"
        file3.write_text("content3")
        add_files_to_zip(str(zip_path), [str(file3)])
        
        # 6. Remove a file
        remove_files_from_zip(str(zip_path), ["file2.txt"])
        
        # 7. Extract remaining files
        extract_dir = temp_dir / "final_extract"
        extract_zip_file(str(zip_path), str(extract_dir))
        
        # 8. Verify final state
        assert (extract_dir / "file1.txt").exists()
        assert not (extract_dir / "file2.txt").exists()
        assert (extract_dir / "file3.txt").exists()
        assert (extract_dir / "file1.txt").read_text() == "content1"
        assert (extract_dir / "file3.txt").read_text() == "content3"

