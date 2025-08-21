"""Unit tests for utils.hash module."""
import pytest
import hashlib
from unittest.mock import patch

from novus_pytils.hash import get_file_md5_hash, get_string_md5_hash


class TestFileMD5Hash:
    """Test file MD5 hash functions."""
    
    def test_get_file_md5_hash_success(self, sample_text_file):
        """Test successful MD5 hash calculation for file."""
        hash_value = get_file_md5_hash(str(sample_text_file))
        
        assert hash_value is not None
        assert len(hash_value) == 32  # MD5 hash is 32 hex characters
        assert all(c in '0123456789abcdef' for c in hash_value.lower())
        
        # Verify by calculating manually
        expected_hash = hashlib.md5(sample_text_file.read_bytes()).hexdigest()
        assert hash_value == expected_hash
    
    def test_get_file_md5_hash_consistent(self, sample_text_file):
        """Test that hash calculation is consistent."""
        hash1 = get_file_md5_hash(str(sample_text_file))
        hash2 = get_file_md5_hash(str(sample_text_file))
        
        assert hash1 == hash2
    
    def test_get_file_md5_hash_different_files(self, temp_dir):
        """Test that different files produce different hashes."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        
        file1.write_text("Content of file 1")
        file2.write_text("Content of file 2")
        
        hash1 = get_file_md5_hash(str(file1))
        hash2 = get_file_md5_hash(str(file2))
        
        assert hash1 != hash2
    
    def test_get_file_md5_hash_empty_file(self, temp_dir):
        """Test MD5 hash of empty file."""
        empty_file = temp_dir / "empty.txt"
        empty_file.touch()
        
        hash_value = get_file_md5_hash(str(empty_file))
        
        # MD5 of empty string/file
        expected_hash = hashlib.md5(b'').hexdigest()
        assert hash_value == expected_hash
    
    def test_get_file_md5_hash_binary_file(self, temp_dir):
        """Test MD5 hash of binary file."""
        binary_file = temp_dir / "binary.bin"
        binary_data = bytes([i % 256 for i in range(1000)])
        binary_file.write_bytes(binary_data)
        
        hash_value = get_file_md5_hash(str(binary_file))
        
        expected_hash = hashlib.md5(binary_data).hexdigest()
        assert hash_value == expected_hash
    
    def test_get_file_md5_hash_large_file(self, temp_dir):
        """Test MD5 hash of larger file."""
        large_file = temp_dir / "large.txt"
        
        # Create a larger file (10KB)
        content = "This is a line of text that will be repeated many times.\n" * 200
        large_file.write_text(content)
        
        hash_value = get_file_md5_hash(str(large_file))
        
        # Read the actual file content as bytes to get the correct hash
        with open(large_file, 'rb') as f:
            actual_content = f.read()
        expected_hash = hashlib.md5(actual_content).hexdigest()
        assert hash_value == expected_hash
    
    def test_get_file_md5_hash_nonexistent_file(self, temp_dir):
        """Test MD5 hash calculation for non-existent file."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError):
            get_file_md5_hash(str(nonexistent_file))
    
    def test_get_file_md5_hash_path_object(self, sample_text_file):
        """Test MD5 hash with Path object input."""
        hash_value = get_file_md5_hash(sample_text_file)
        
        assert hash_value is not None
        assert len(hash_value) == 32
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_get_file_md5_hash_permission_error(self, mock_file):
        """Test MD5 hash calculation with permission error."""
        with pytest.raises(PermissionError):
            get_file_md5_hash("some_file.txt")
    
    @patch('builtins.open', side_effect=IOError("I/O error"))
    def test_get_file_md5_hash_io_error(self, mock_file):
        """Test MD5 hash calculation with I/O error."""
        with pytest.raises(IOError):
            get_file_md5_hash("some_file.txt")


class TestStringMD5Hash:
    """Test string MD5 hash functions."""
    
    def test_get_string_md5_hash_basic(self):
        """Test basic string MD5 hash calculation."""
        test_string = "Hello, World!"
        hash_value = get_string_md5_hash(test_string)
        
        assert hash_value is not None
        assert len(hash_value) == 32
        assert all(c in '0123456789abcdef' for c in hash_value.lower())
        
        # Verify by calculating manually
        expected_hash = hashlib.md5(test_string.encode()).hexdigest()
        assert hash_value == expected_hash
    
    def test_get_string_md5_hash_empty_string(self):
        """Test MD5 hash of empty string."""
        hash_value = get_string_md5_hash("")
        
        expected_hash = hashlib.md5(b'').hexdigest()
        assert hash_value == expected_hash
    
    def test_get_string_md5_hash_unicode(self):
        """Test MD5 hash of Unicode string."""
        unicode_string = "Hello, 世界! 🌍"
        hash_value = get_string_md5_hash(unicode_string)
        
        expected_hash = hashlib.md5(unicode_string.encode('utf-8')).hexdigest()
        assert hash_value == expected_hash
    
    def test_get_string_md5_hash_multiline(self):
        """Test MD5 hash of multiline string."""
        multiline_string = """This is line 1
This is line 2
This is line 3"""
        hash_value = get_string_md5_hash(multiline_string)
        
        expected_hash = hashlib.md5(multiline_string.encode()).hexdigest()
        assert hash_value == expected_hash
    
    def test_get_string_md5_hash_special_characters(self):
        """Test MD5 hash with special characters."""
        special_string = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        hash_value = get_string_md5_hash(special_string)
        
        expected_hash = hashlib.md5(special_string.encode()).hexdigest()
        assert hash_value == expected_hash
    
    def test_get_string_md5_hash_very_long_string(self):
        """Test MD5 hash of very long string."""
        long_string = "A" * 10000  # 10,000 characters
        hash_value = get_string_md5_hash(long_string)
        
        expected_hash = hashlib.md5(long_string.encode()).hexdigest()
        assert hash_value == expected_hash
    
    def test_get_string_md5_hash_consistent(self):
        """Test that string hash calculation is consistent."""
        test_string = "Consistency test"
        
        hash1 = get_string_md5_hash(test_string)
        hash2 = get_string_md5_hash(test_string)
        
        assert hash1 == hash2
    
    def test_get_string_md5_hash_different_strings(self):
        """Test that different strings produce different hashes."""
        string1 = "String one"
        string2 = "String two"
        
        hash1 = get_string_md5_hash(string1)
        hash2 = get_string_md5_hash(string2)
        
        assert hash1 != hash2
    
    def test_get_string_md5_hash_case_sensitive(self):
        """Test that string hash is case sensitive."""
        string1 = "CaseSensitive"
        string2 = "casesensitive"
        
        hash1 = get_string_md5_hash(string1)
        hash2 = get_string_md5_hash(string2)
        
        assert hash1 != hash2
    
    def test_get_string_md5_hash_whitespace_sensitive(self):
        """Test that string hash is whitespace sensitive."""
        string1 = "whitespace test"
        string2 = "whitespace  test"  # Extra space
        string3 = " whitespace test"  # Leading space
        
        hash1 = get_string_md5_hash(string1)
        hash2 = get_string_md5_hash(string2)
        hash3 = get_string_md5_hash(string3)
        
        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3


class TestHashFunctionIntegration:
    """Test integration between file and string hash functions."""
    
    def test_file_and_string_hash_equivalence(self, temp_dir):
        """Test that file hash matches string hash of file content."""
        content = "This is test content for hash comparison"
        test_file = temp_dir / "hash_test.txt"
        test_file.write_text(content)
        
        file_hash = get_file_md5_hash(str(test_file))
        string_hash = get_string_md5_hash(content)
        
        assert file_hash == string_hash
    
    def test_binary_file_hash_consistency(self, temp_dir):
        """Test hash consistency for binary files."""
        binary_data = bytes([i % 256 for i in range(100)])
        binary_file = temp_dir / "binary_test.bin"
        binary_file.write_bytes(binary_data)
        
        file_hash = get_file_md5_hash(str(binary_file))
        
        # Calculate expected hash
        expected_hash = hashlib.md5(binary_data).hexdigest()
        assert file_hash == expected_hash


class TestHashFunctionEdgeCases:
    """Test edge cases for hash functions."""
    
    def test_hash_with_none_input(self):
        """Test hash function behavior with None input."""
        with pytest.raises((TypeError, AttributeError)):
            get_string_md5_hash(None)
    
    def test_hash_with_number_input(self):
        """Test hash function with numeric input."""
        # Should work if converted to string first
        hash_value = get_string_md5_hash(str(12345))
        expected_hash = hashlib.md5("12345".encode()).hexdigest()
        assert hash_value == expected_hash
    
    def test_file_hash_with_special_filename(self, temp_dir):
        """Test file hash with special characters in filename."""
        special_file = temp_dir / "special-file_name.txt"
        special_file.write_text("Content with special filename")
        
        hash_value = get_file_md5_hash(str(special_file))
        assert hash_value is not None
        assert len(hash_value) == 32


@pytest.mark.slow
class TestHashPerformance:
    """Performance tests for hash functions."""
    
    def test_large_file_hash_performance(self, temp_dir):
        """Test performance of hashing large files."""
        large_file = temp_dir / "large_file.txt"
        
        # Create a 1MB file
        content = "x" * (1024 * 1024)  # 1MB of 'x' characters
        large_file.write_text(content)
        
        import time
        start_time = time.time()
        
        hash_value = get_file_md5_hash(str(large_file))
        
        end_time = time.time()
        hash_time = end_time - start_time
        
        assert hash_value is not None
        assert len(hash_value) == 32
        # Should complete within reasonable time (adjust threshold as needed)
        assert hash_time < 5.0  # 5 seconds for 1MB should be reasonable
    
    def test_many_small_hashes_performance(self):
        """Test performance of many small hash calculations."""
        import time
        
        start_time = time.time()
        
        # Calculate 1000 small string hashes
        for i in range(1000):
            hash_value = get_string_md5_hash(f"test string {i}")
            assert len(hash_value) == 32
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete reasonably quickly
        assert total_time < 2.0  # 2 seconds for 1000 small hashes