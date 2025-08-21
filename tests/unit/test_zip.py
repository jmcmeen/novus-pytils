from novus_pytils.zip import extract_zip_file
import pytest

class TestExtractZip:
    """Test extract_zip function."""
    
    def test_extract_zip_success(self, temp_dir):
        """Test successful ZIP extraction."""
        import zipfile
        
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

