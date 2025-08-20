"""Unit tests for handlers.text_handler module."""
import pytest
from unittest.mock import patch, mock_open

from novus_pytils.models.handlers.text_handler import TextHandler
from novus_pytils.utils.exceptions import FileHandlerError, UnsupportedFormatError

class TestTextHandler:
    """Test TextHandler class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.handler = TextHandler()
    
    def test_init(self):
        """Test TextHandler initialization."""
        assert isinstance(self.handler, TextHandler)
        assert hasattr(self.handler, 'supported_extensions')
    
    @patch('builtins.open', new_callable=mock_open, read_data='test content')
    def test_read_success(self, mock_file):
        """Test successful file reading."""
        result = self.handler.read('test.txt')
        
        assert result == 'test content'
        mock_file.assert_called_once_with('test.txt', 'r', encoding='utf-8')
    
    @patch('builtins.open', new_callable=mock_open, read_data='test content')
    def test_read_with_custom_encoding(self, mock_file):
        """Test file reading with custom encoding."""
        result = self.handler.read('test.txt', encoding='latin-1')
        
        assert result == 'test content'
        mock_file.assert_called_once_with('test.txt', 'r', encoding='latin-1')
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_read_file_not_found(self, mock_file):
        """Test reading non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.handler.read('nonexistent.txt')
    
    @patch('builtins.open', new_callable=mock_open)
    def test_write_success(self, mock_file):
        """Test successful file writing."""
        result = self.handler.write('test.txt', 'test content')
        
        assert result is True
        mock_file.assert_called_once_with('test.txt', 'w', encoding='utf-8')
        mock_file().write.assert_called_once_with('test content')
    
    @patch('builtins.open', new_callable=mock_open)
    def test_write_with_custom_encoding(self, mock_file):
        """Test file writing with custom encoding."""
        result = self.handler.write('test.txt', 'test content', encoding='latin-1')
        
        assert result is True
        mock_file.assert_called_once_with('test.txt', 'w', encoding='latin-1')
    
    @patch('builtins.open', side_effect=PermissionError())
    def test_write_permission_error(self, mock_file):
        """Test writing with permission error."""
        with pytest.raises(PermissionError):
            self.handler.write('readonly.txt', 'content')
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_new_file(self, mock_file, mock_exists):
        """Test creating new file."""
        mock_exists.return_value = False
        
        result = self.handler.create('new_file.txt', 'initial content')
        
        assert result is True
        mock_file.assert_called_once_with('new_file.txt', 'w', encoding='utf-8')
    
    @patch('os.path.exists')
    def test_create_file_already_exists(self, mock_exists):
        """Test creating file that already exists."""
        mock_exists.return_value = True
        
        with pytest.raises(FileHandlerError):
            self.handler.create('existing.txt', 'content')
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_update_existing_file(self, mock_file, mock_exists):
        """Test updating existing file."""
        mock_exists.return_value = True
        
        result = self.handler.update('existing.txt', 'updated content')
        
        assert result is True
        mock_file.assert_called_once_with('existing.txt', 'w', encoding='utf-8')
    
    @patch('os.path.exists')
    def test_update_nonexistent_file(self, mock_exists):
        """Test updating non-existent file."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            self.handler.update('nonexistent.txt', 'content')
    
    @patch('os.remove')
    @patch('os.path.exists')
    def test_delete_success(self, mock_exists, mock_remove):
        """Test successful file deletion."""
        mock_exists.return_value = True
        
        result = self.handler.delete('test.txt')
        
        assert result is True
        mock_remove.assert_called_once_with('test.txt')
    
    @patch('os.path.exists')
    def test_delete_nonexistent_file(self, mock_exists):
        """Test deleting non-existent file."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            self.handler.delete('nonexistent.txt')
    
    @patch('shutil.copy2')
    @patch('os.path.exists')
    def test_copy_success(self, mock_exists, mock_copy):
        """Test successful file copying."""
        mock_exists.return_value = True
        
        result = self.handler.copy('source.txt', 'destination.txt')
        
        assert result is True
        mock_copy.assert_called_once_with('source.txt', 'destination.txt')
    
    @patch('shutil.move')
    @patch('os.path.exists')
    def test_move_success(self, mock_exists, mock_move):
        """Test successful file moving."""
        mock_exists.return_value = True
        
        result = self.handler.move('source.txt', 'destination.txt')
        
        assert result is True
        mock_move.assert_called_once_with('source.txt', 'destination.txt')
    
    @patch('builtins.open', new_callable=mock_open, read_data='line1\nline2\nline3\n')
    def test_convert_to_html(self, mock_file):
        """Test converting text to HTML."""
        with patch('builtins.open', mock_open()) as mock_output:
            result = self.handler.convert('input.txt', 'output.html', '.html')
            
            assert result is True
            # Verify HTML structure was written
            mock_output().write.assert_called()
    
    @patch('builtins.open', new_callable=mock_open, read_data='test,data,here\n1,2,3\n')
    def test_convert_csv_to_json(self, mock_file):
        """Test converting CSV to JSON."""
        with patch('builtins.open', mock_open()) as mock_output:
            result = self.handler.convert('input.csv', 'output.json', '.json')
            
            assert result is True
            mock_output().write.assert_called()
    
    def test_convert_unsupported_format(self):
        """Test converting to unsupported format."""
        with pytest.raises(UnsupportedFormatError):
            self.handler.convert('input.txt', 'output.xyz', '.xyz')
    
    @patch('os.path.getsize')
    @patch('os.path.getmtime')
    @patch('os.path.exists')
    def test_get_metadata(self, mock_exists, mock_getmtime, mock_getsize):
        """Test getting file metadata."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_getmtime.return_value = 1234567890
        
        with patch('builtins.open', mock_open(read_data='line1\nline2\nline3\n')):
            metadata = self.handler.get_metadata('test.txt')
        
        assert metadata['size'] == 1024
        assert metadata['modified_time'] == 1234567890
        assert metadata['line_count'] == 3
        assert metadata['extension'] == '.txt'
    
    def test_get_supported_conversions(self):
        """Test getting supported conversion formats."""
        conversions = self.handler.get_supported_conversions('.txt')
        
        assert isinstance(conversions, list)
        assert '.html' in conversions
        assert '.md' in conversions
        assert '.json' in conversions
    
    def test_get_supported_conversions_unsupported(self):
        """Test getting conversions for unsupported extension."""
        conversions = self.handler.get_supported_conversions('.xyz')
        
        assert conversions == []
    
    @patch('builtins.open', new_callable=mock_open, read_data='file1 content\n')
    def test_merge_files(self, mock_file):
        """Test merging multiple text files."""
        with patch('builtins.open', mock_open()) as mock_output:
            result = self.handler.merge_files(
                ['file1.txt', 'file2.txt'], 
                'merged.txt', 
                separator='\n---\n'
            )
            
            assert result is True
            mock_output().write.assert_called()
    
    @patch('builtins.open', new_callable=mock_open, read_data='line1\nline2\nline3\nline4\nline5\n')
    def test_split_file(self, mock_file):
        """Test splitting text file into parts."""
        with patch('builtins.open', mock_open()):
            result = self.handler.split_file('input.txt', '/output', lines_per_file=2)
            
            assert isinstance(result, list)
            assert len(result) > 0
    
    @patch('builtins.open', new_callable=mock_open, read_data='word1 word2 word3\nline2 content\n')
    def test_get_text_statistics(self, mock_file):
        """Test getting text statistics."""
        stats = self.handler.get_text_statistics('test.txt')
        
        assert 'line_count' in stats
        assert 'word_count' in stats
        assert 'char_count' in stats
        assert stats['line_count'] == 2
        assert stats['word_count'] >= 5
    
    @patch('builtins.open', new_callable=mock_open, read_data='Hello world\nThis is a test\n')
    def test_search_text(self, mock_file):
        """Test searching text in file."""
        results = self.handler.search_text('test.txt', 'test')
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert 'line_number' in results[0]
        assert 'line_content' in results[0]
    
    @patch('builtins.open', new_callable=mock_open, read_data='Hello world\nThis is old text\n')
    def test_replace_text(self, mock_file):
        """Test replacing text in file."""
        with patch('builtins.open', mock_open()) as mock_output:
            result = self.handler.replace_text('test.txt', 'old', 'new')
            
            assert result is True
            mock_output().write.assert_called()
    
    def test_validate_encoding(self):
        """Test encoding validation."""
        assert self.handler._validate_encoding('utf-8') is True
        assert self.handler._validate_encoding('ascii') is True
        assert self.handler._validate_encoding('latin-1') is True
        assert self.handler._validate_encoding('invalid-encoding') is False
    
    def test_detect_encoding(self):
        """Test encoding detection."""
        # This test would require the chardet library
        # For now, just test that the method exists and returns a string
        with patch('builtins.open', mock_open(read_data=b'test content')):
            encoding = self.handler._detect_encoding('test.txt')
            assert isinstance(encoding, str)
    
    def test_normalize_line_endings(self):
        """Test line ending normalization."""
        # Test Unix to Windows
        result = self.handler._normalize_line_endings('line1\nline2\n', 'windows')
        assert '\r\n' in result
        
        # Test Windows to Unix  
        result = self.handler._normalize_line_endings('line1\r\nline2\r\n', 'unix')
        assert '\r\n' not in result
        assert '\n' in result