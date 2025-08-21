"""Unit tests for api.object_oriented module."""
import pytest
from unittest.mock import patch, MagicMock

from novus_pytils.models.models import (
    FileManager, File, FileBatch, MediaCollection, BaseFileHandler,
    FileManagerMixin, ValidationResult, ColorCode
)
from novus_pytils.models.exceptions import FileHandlerError, UnsupportedFormatError

class TestBaseFileHandler:
    """Test BaseFileHandler abstract class."""
    
    def test_cannot_instantiate_directly(self):
        """Test that BaseFileHandler cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseFileHandler()
    
    def test_subclass_must_implement_abstract_methods(self):
        """Test that subclasses must implement abstract methods."""
        
        class IncompleteHandler(BaseFileHandler):
            pass
        
        with pytest.raises(TypeError):
            IncompleteHandler()
    
    def test_complete_subclass_can_be_instantiated(self):
        """Test that complete subclass can be instantiated."""
        
        class CompleteHandler(BaseFileHandler):
            def read(self, file_path, **kwargs):
                return "content"
            
            def write(self, file_path, content, **kwargs):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                return True
        
        # Should not raise exception
        handler = CompleteHandler()
        assert isinstance(handler, BaseFileHandler)
    
    @patch('os.path.exists')
    @patch('os.stat')
    def test_subclass_methods_work(self, mock_stat, mock_exists):
        """Test that BaseFileHandler methods work correctly."""
        
        class TestHandler(BaseFileHandler):
            def read(self, file_path, **kwargs):
                return "content"
            
            def write(self, file_path, content, **kwargs):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                if target_format == ".xyz":
                    return False
                return True
        
        handler = TestHandler()
        handler.supported_extensions = [".txt", ".pdf"]
        handler.conversion_map = {".txt": [".pdf", ".docx", ".html"]}
        
        # Test validate_file method
        mock_exists.return_value = True
        assert handler.validate_file("test.txt") is True
        
        mock_exists.return_value = False
        assert handler.validate_file("test.txt") is False
        
        # Test with unsupported extension
        mock_exists.return_value = True
        assert handler.validate_file("test.xyz") is False
        
        # Test convert method (implemented by subclass)
        assert handler.convert("input.txt", "output.pdf", ".pdf") is True
        assert handler.convert("input.txt", "output.xyz", ".xyz") is False
        
        # Test get_metadata method
        stat_result = type('StatResult', (), {
            'st_size': 1024,
            'st_ctime': 1234567890,
            'st_mtime': 1234567891,
            'st_atime': 1234567892
        })()
        mock_stat.return_value = stat_result
        mock_exists.return_value = True
        
        metadata = handler.get_metadata("test.txt")
        assert metadata["size"] == 1024
        assert metadata["extension"] == ".txt"
        assert metadata["basename"] == "test.txt"
        
        # Test get_supported_conversions method
        conversions = handler.get_supported_conversions(".txt")
        assert ".pdf" in conversions
        assert ".docx" in conversions
        assert ".html" in conversions
        
        conversions = handler.get_supported_conversions(".unknown")
        assert conversions == []


class TestBaseFileHandlerMethods:
    """Test BaseFileHandler actual methods."""
    
    def setup_method(self):
        """Setup test handler."""
        class TestHandler(BaseFileHandler):
            def read(self, file_path, **kwargs):
                return "content"
            
            def write(self, file_path, content, **kwargs):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                return True
        
        self.handler = TestHandler()
    
    @patch('os.path.exists')
    def test_validate_file_exists_and_supported(self, mock_exists):
        """Test file validation when file exists and is supported."""
        mock_exists.return_value = True
        self.handler.supported_extensions = ['.txt']
        
        result = self.handler.validate_file("existing_file.txt")
        assert result is True
        mock_exists.assert_called_once_with("existing_file.txt")
    
    @patch('os.path.exists')
    def test_validate_file_not_exists(self, mock_exists):
        """Test file validation when file doesn't exist."""
        mock_exists.return_value = False
        self.handler.supported_extensions = ['.txt']
        
        result = self.handler.validate_file("nonexistent_file.txt")
        assert result is False
    
    @patch('os.path.exists')  
    def test_validate_file_unsupported_extension(self, mock_exists):
        """Test file validation with unsupported extension."""
        mock_exists.return_value = True
        self.handler.supported_extensions = ['.txt', '.pdf']
        
        result = self.handler.validate_file("document.xyz")
        assert result is False
    
    def test_get_supported_conversions(self):
        """Test getting supported conversions."""
        self.handler.conversion_map = {".txt": [".pdf", ".docx"], ".jpg": [".png", ".gif"]}
        
        conversions = self.handler.get_supported_conversions(".txt")
        assert ".pdf" in conversions
        assert ".docx" in conversions
        
        conversions = self.handler.get_supported_conversions(".unknown")
        assert conversions == []
    
    @patch('os.stat')
    @patch('os.path.exists')
    def test_get_metadata_success(self, mock_exists, mock_stat):
        """Test getting file metadata successfully."""
        mock_exists.return_value = True
        
        stat_result = type('StatResult', (), {
            'st_size': 1024,
            'st_ctime': 1234567890,
            'st_mtime': 1234567891,
            'st_atime': 1234567892
        })()
        mock_stat.return_value = stat_result
        
        metadata = self.handler.get_metadata("test.txt")
        
        assert metadata['size'] == 1024
        assert metadata['extension'] == '.txt'
        assert metadata['basename'] == 'test.txt'
        assert 'created' in metadata
        assert 'modified' in metadata
        assert 'accessed' in metadata
    
    @patch('os.path.exists')
    def test_get_metadata_file_not_exists(self, mock_exists):
        """Test getting metadata for nonexistent file."""
        mock_exists.return_value = False
        
        with pytest.raises(FileHandlerError):
            self.handler.get_metadata("nonexistent.txt")

class TestFileManager:
    """Test FileManager class."""
    
    def test_init(self):
        """Test FileManager initialization."""
        manager = FileManager()
        assert 'text' in manager._handlers
        assert 'image' in manager._handlers
        assert 'audio' in manager._handlers
        assert 'video' in manager._handlers
        assert isinstance(manager._cache, dict)
    
    @patch('novus_pytils.globals.SUPPORTED_TEXT_EXTENSIONS', ['.txt'])
    def test_get_handler_text(self):
        """Test getting text handler."""
        manager = FileManager()
        handler, file_type = manager._get_handler('test.txt')
        assert file_type == 'text'
        assert handler == manager._handlers['text']
    
    @patch('novus_pytils.globals.SUPPORTED_IMAGE_EXTENSIONS', ['.jpg'])
    def test_get_handler_image(self):
        """Test getting image handler."""
        manager = FileManager()
        handler, file_type = manager._get_handler('test.jpg')
        assert file_type == 'image'
        assert handler == manager._handlers['image']
    
    def test_get_handler_unsupported(self):
        """Test getting handler for unsupported format."""
        manager = FileManager()
        with pytest.raises(UnsupportedFormatError):
            manager._get_handler('test.unknown')
    
    def test_get_file(self):
        """Test getting File object."""
        manager = FileManager()
        file_obj = manager.get_file('test.txt')
        assert isinstance(file_obj, File)
        assert file_obj.path == 'test.txt'
        assert file_obj.manager == manager
    
    def test_get_batch(self):
        """Test getting FileBatch object."""
        manager = FileManager()
        batch = manager.get_batch(['file1.txt', 'file2.txt'])
        assert isinstance(batch, FileBatch)
        assert batch.paths == ['file1.txt', 'file2.txt']
        assert batch.manager == manager


class TestFile:
    """Test File class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.manager = FileManager()
        self.file = File('test.txt', self.manager)
    
    @patch('os.path.exists')
    def test_exists_property(self, mock_exists):
        """Test exists property."""
        mock_exists.return_value = True
        assert self.file.exists is True
        mock_exists.assert_called_once_with('test.txt')
    
    def test_extension_property(self):
        """Test extension property."""
        assert self.file.extension == '.txt'
    
    def test_basename_property(self):
        """Test basename property."""
        assert self.file.basename == 'test.txt'
    
    @patch('os.path.dirname')
    def test_directory_property(self, mock_dirname):
        """Test directory property."""
        mock_dirname.return_value = '/path/to'
        assert self.file.directory == '/path/to'
        mock_dirname.assert_called_once_with('test.txt')
    
    @patch('novus_pytils.globals.SUPPORTED_TEXT_EXTENSIONS', ['.txt'])
    def test_file_type_property(self):
        """Test file_type property."""
        assert self.file.file_type == 'text'
    
    def test_file_type_property_unknown(self):
        """Test file_type property for unknown format."""
        file_obj = File('test.unknown', self.manager)
        assert file_obj.file_type == 'unknown'
    
    @patch.object(FileManager, '_get_handler')
    def test_read(self, mock_get_handler):
        """Test reading file."""
        mock_handler = MagicMock()
        mock_handler.read.return_value = "test content"
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.read()
        
        assert result == self.file
        assert self.file._cached_content == "test content"
        mock_handler.read.assert_called_once_with('test.txt')
    
    @patch.object(FileManager, '_get_handler')
    def test_write_with_content(self, mock_get_handler):
        """Test writing file with content."""
        mock_handler = MagicMock()
        mock_handler.write.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.write("new content")
        
        assert result == self.file
        assert self.file._cached_content == "new content"
        assert self.file._modified is True
        mock_handler.write.assert_called_once_with('test.txt', "new content")
    
    @patch.object(FileManager, '_get_handler')
    def test_write_with_cached_content(self, mock_get_handler):
        """Test writing file with cached content."""
        mock_handler = MagicMock()
        mock_handler.write.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        self.file._cached_content = "cached content"
        result = self.file.write()
        
        assert result == self.file
        assert self.file._modified is True
        mock_handler.write.assert_called_once_with('test.txt', "cached content")
    
    @patch.object(FileManager, '_get_handler')
    def test_write_no_content(self, mock_get_handler):
        """Test writing file without content raises error."""
        mock_handler = MagicMock()
        mock_get_handler.return_value = (mock_handler, 'text')
        
        with pytest.raises(FileHandlerError):
            self.file.write()
    
    @patch.object(FileManager, '_get_handler')
    def test_create(self, mock_get_handler):
        """Test creating file."""
        mock_handler = MagicMock()
        mock_handler.create.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.create("content")
        
        assert result == self.file
        assert self.file._cached_content == "content"
        mock_handler.create.assert_called_once_with('test.txt', "content")
    
    @patch.object(FileManager, '_get_handler')
    def test_update(self, mock_get_handler):
        """Test updating file."""
        mock_handler = MagicMock()
        mock_handler.update.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.update("new content")
        
        assert result == self.file
        assert self.file._cached_content == "new content"
        assert self.file._modified is True
        mock_handler.update.assert_called_once_with('test.txt', "new content")
    
    @patch.object(FileManager, '_get_handler')
    def test_delete(self, mock_get_handler):
        """Test deleting file."""
        mock_handler = MagicMock()
        mock_handler.delete.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.delete()
        
        assert result == self.file
        assert self.file._cached_content is None
        mock_handler.delete.assert_called_once_with('test.txt')
    
    @patch.object(FileManager, '_get_handler')
    def test_copy_to(self, mock_get_handler):
        """Test copying file."""
        mock_handler = MagicMock()
        mock_handler.copy.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.copy_to('dest.txt')
        
        assert isinstance(result, File)
        assert result.path == 'dest.txt'
        assert result.manager == self.manager
        mock_handler.copy.assert_called_once_with('test.txt', 'dest.txt')
    
    @patch.object(FileManager, '_get_handler')
    def test_move_to(self, mock_get_handler):
        """Test moving file."""
        mock_handler = MagicMock()
        mock_handler.move.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.move_to('dest.txt')
        
        assert result == self.file
        assert self.file.path == 'dest.txt'
        mock_handler.move.assert_called_once_with('test.txt', 'dest.txt')
    
    @patch.object(FileManager, '_get_handler')
    def test_convert_to(self, mock_get_handler):
        """Test converting file."""
        mock_handler = MagicMock()
        mock_handler.convert.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.convert_to('output.pdf', '.pdf')
        
        assert isinstance(result, File)
        assert result.path == 'output.pdf'
        mock_handler.convert.assert_called_once_with('test.txt', 'output.pdf', '.pdf')
    
    @patch.object(FileManager, '_get_handler')
    def test_get_info_text(self, mock_get_handler):
        """Test getting file info for text file."""
        mock_handler = MagicMock()
        mock_handler.get_metadata.return_value = {'size': 1024}
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.get_info()
        
        assert result == {'size': 1024}
        mock_handler.get_metadata.assert_called_once_with('test.txt')
    
    @patch.object(FileManager, '_get_handler')
    def test_get_info_image(self, mock_get_handler):
        """Test getting file info for image file."""
        mock_handler = MagicMock()
        mock_handler.get_image_info.return_value = {'width': 100, 'height': 100}
        mock_get_handler.return_value = (mock_handler, 'image')
        
        file_obj = File('test.jpg', self.manager)
        result = file_obj.get_info()
        
        assert result == {'width': 100, 'height': 100}
        mock_handler.get_image_info.assert_called_once_with('test.jpg')
    
    @patch.object(FileManager, '_get_handler')
    def test_get_supported_conversions(self, mock_get_handler):
        """Test getting supported conversions."""
        mock_handler = MagicMock()
        mock_handler.get_supported_conversions.return_value = ['.pdf', '.docx']
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = self.file.get_supported_conversions()
        
        assert result == ['.pdf', '.docx']
        mock_handler.get_supported_conversions.assert_called_once_with('.txt')
    
    @patch.object(File, 'read')
    def test_content_property_cached(self, mock_read):
        """Test content property with cached content."""
        self.file._cached_content = "cached"
        result = self.file.content
        assert result == "cached"
        mock_read.assert_not_called()
    
    @patch.object(File, 'read')
    def test_content_property_not_cached(self, mock_read):
        """Test content property without cached content."""
        mock_read.return_value = self.file
        self.file._cached_content = None
        _ = self.file.content
        mock_read.assert_called_once()
    
    @patch('novus_pytils.globals.SUPPORTED_IMAGE_EXTENSIONS', ['.jpg'])
    @patch.object(FileManager, '_get_handler')
    def test_resize(self, mock_get_handler):
        """Test resizing image."""
        mock_handler = MagicMock()
        mock_handler.resize.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        
        file_obj = File('test.jpg', self.manager)
        result = file_obj.resize((100, 100))
        
        assert result == file_obj
        assert file_obj._cached_content is None
        mock_handler.resize.assert_called_once_with('test.jpg', 'test.jpg', (100, 100), True)
    
    def test_resize_not_image(self):
        """Test resizing non-image file raises error."""
        with pytest.raises(UnsupportedFormatError):
            self.file.resize((100, 100))
    
    @patch('novus_pytils.globals.SUPPORTED_IMAGE_EXTENSIONS', ['.jpg'])
    @patch.object(FileManager, '_get_handler')
    def test_resize_to(self, mock_get_handler):
        """Test resizing image to new file."""
        mock_handler = MagicMock()
        mock_handler.resize.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        
        file_obj = File('test.jpg', self.manager)
        result = file_obj.resize_to('output.jpg', (100, 100))
        
        assert isinstance(result, File)
        assert result.path == 'output.jpg'
        mock_handler.resize.assert_called_once_with('test.jpg', 'output.jpg', (100, 100), True)
    
    @patch('novus_pytils.globals.SUPPORTED_AUDIO_EXTENSIONS', ['.mp3'])
    @patch.object(FileManager, '_get_handler')
    def test_trim_audio(self, mock_get_handler):
        """Test trimming audio."""
        mock_handler = MagicMock()
        mock_handler.trim.return_value = True
        mock_get_handler.return_value = (mock_handler, 'audio')
        
        file_obj = File('test.mp3', self.manager)
        result = file_obj.trim(1000, 5000)
        
        assert result == file_obj
        assert file_obj._cached_content is None
        mock_handler.trim.assert_called_once_with('test.mp3', 'test.mp3', 1000, 5000)
    
    def test_trim_unsupported(self):
        """Test trimming unsupported file type."""
        with pytest.raises(UnsupportedFormatError):
            self.file.trim(1000, 5000)
    
    @patch('novus_pytils.globals.SUPPORTED_IMAGE_EXTENSIONS', ['.jpg'])
    @patch.object(FileManager, '_get_handler')
    def test_apply_filter(self, mock_get_handler):
        """Test applying filter."""
        mock_handler = MagicMock()
        mock_handler.apply_filter.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        
        file_obj = File('test.jpg', self.manager)
        result = file_obj.apply_filter('blur')
        
        assert result == file_obj
        assert file_obj._cached_content is None
        mock_handler.apply_filter.assert_called_once_with('test.jpg', 'test.jpg', 'blur')
    
    def test_apply_filter_unsupported(self):
        """Test applying filter to unsupported file type."""
        with pytest.raises(UnsupportedFormatError):
            self.file.apply_filter('blur')
    
    @patch('novus_pytils.globals.SUPPORTED_IMAGE_EXTENSIONS', ['.jpg'])
    @patch.object(FileManager, '_get_handler')
    def test_create_thumbnail_image(self, mock_get_handler):
        """Test creating thumbnail from image."""
        mock_handler = MagicMock()
        mock_handler.create_thumbnail.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        
        file_obj = File('test.jpg', self.manager)
        result = file_obj.create_thumbnail('thumb.jpg', size=(64, 64))
        
        assert isinstance(result, File)
        assert result.path == 'thumb.jpg'
        mock_handler.create_thumbnail.assert_called_once_with('test.jpg', 'thumb.jpg', (64, 64), size=(64, 64))
    
    @patch.object(File, 'read')
    @patch.object(File, 'write')
    def test_editing_context_manager(self, mock_write, mock_read):
        """Test editing context manager."""
        self.file._cached_content = "content"
        self.file._modified = True
        mock_read.return_value = self.file
        mock_write.return_value = self.file
        
        with self.file.editing() as f:
            assert f == self.file
        
        mock_write.assert_called_once()
    
    def test_str_representation(self):
        """Test string representation."""
        assert str(self.file) == "File(test.txt)"
    
    @patch('os.path.exists')
    def test_repr_representation(self, mock_exists):
        """Test repr representation."""
        mock_exists.return_value = True
        result = repr(self.file)
        assert "File(path='test.txt'" in result
        assert "exists=True" in result


class TestFileBatch:
    """Test FileBatch class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.manager = FileManager()
        self.batch = FileBatch(['file1.txt', 'file2.txt'], self.manager)
    
    def test_init(self):
        """Test FileBatch initialization."""
        assert self.batch.paths == ['file1.txt', 'file2.txt']
        assert self.batch.manager == self.manager
        assert len(self.batch._files) == 2
        assert all(isinstance(f, File) for f in self.batch._files)
    
    def test_files_property(self):
        """Test files property."""
        files = self.batch.files
        assert files == self.batch._files
        assert len(files) == 2
    
    @patch.object(File, 'convert_to')
    @patch('os.path.splitext')
    def test_convert_all_with_output_dir(self, mock_splitext, mock_convert):
        """Test converting all files with output directory."""
        mock_splitext.return_value = ('file1', '.txt')
        mock_convert.return_value = File('output.pdf', self.manager)
        
        result = self.batch.convert_all('.pdf', '/output')
        
        assert result == {'file1.txt': True, 'file2.txt': True}
    
    @patch.object(File, 'convert_to')
    @patch('os.path.splitext')
    def test_convert_all_without_output_dir(self, mock_splitext, mock_convert):
        """Test converting all files without output directory."""
        mock_splitext.return_value = ('file1', '.txt')
        mock_convert.return_value = File('file1.pdf', self.manager)
        
        result = self.batch.convert_all('.pdf')
        
        assert result == {'file1.txt': True, 'file2.txt': True}
    
    @patch.object(File, 'convert_to')
    def test_convert_all_with_exception(self, mock_convert):
        """Test converting all files with exception."""
        mock_convert.side_effect = Exception("Error")
        
        result = self.batch.convert_all('.pdf')
        
        assert result == {'file1.txt': False, 'file2.txt': False}
    
    @patch.object(File, 'copy_to')
    def test_copy_all(self, mock_copy):
        """Test copying all files."""
        mock_copy.return_value = File('dest/file1.txt', self.manager)
        
        result = self.batch.copy_all('/dest')
        
        assert result == {'file1.txt': True, 'file2.txt': True}
    
    @patch.object(File, 'move_to')
    def test_move_all(self, mock_move):
        """Test moving all files."""
        mock_move.return_value = File('dest/file1.txt', self.manager)
        
        result = self.batch.move_all('/dest')
        
        assert result == {'file1.txt': True, 'file2.txt': True}
    
    @patch.object(File, 'delete')
    def test_delete_all(self, mock_delete):
        """Test deleting all files."""
        mock_delete.return_value = File('file1.txt', self.manager)
        
        result = self.batch.delete_all()
        
        assert result == {'file1.txt': True, 'file2.txt': True}
    
    @patch.object(File, 'get_info')
    def test_get_all_info(self, mock_get_info):
        """Test getting info for all files."""
        mock_get_info.return_value = {'size': 1024}
        
        result = self.batch.get_all_info()
        
        assert result == {'file1.txt': {'size': 1024}, 'file2.txt': {'size': 1024}}
    
    @patch.object(File, 'get_info')
    def test_get_all_info_with_exception(self, mock_get_info):
        """Test getting info for all files with exception."""
        mock_get_info.side_effect = Exception("Error")
        
        result = self.batch.get_all_info()
        
        assert result == {'file1.txt': {}, 'file2.txt': {}}
    
    @patch('novus_pytils.globals.SUPPORTED_TEXT_EXTENSIONS', ['.txt'])
    def test_filter_by_type(self):
        """Test filtering by file type."""
        result = self.batch.filter_by_type('text')
        
        assert isinstance(result, FileBatch)
        assert len(result) == 2
    
    def test_filter_by_extension(self):
        """Test filtering by extension."""
        result = self.batch.filter_by_extension('.txt')
        
        assert isinstance(result, FileBatch)
        assert len(result) == 2
    
    def test_filter_by_extension_without_dot(self):
        """Test filtering by extension without dot."""
        result = self.batch.filter_by_extension('txt')
        
        assert isinstance(result, FileBatch)
        assert len(result) == 2
    
    def test_len(self):
        """Test length."""
        assert len(self.batch) == 2
    
    def test_iter(self):
        """Test iteration."""
        files = list(self.batch)
        assert len(files) == 2
        assert all(isinstance(f, File) for f in files)
    
    def test_getitem(self):
        """Test indexing."""
        file_obj = self.batch[0]
        assert isinstance(file_obj, File)
        assert file_obj.path == 'file1.txt'
    
    def test_str_representation(self):
        """Test string representation."""
        assert str(self.batch) == "FileBatch(2 files)"
    
    def test_repr_representation(self):
        """Test repr representation."""
        result = repr(self.batch)
        assert "FileBatch(count=2" in result


class TestMediaCollection:
    """Test MediaCollection class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.manager = FileManager()
        self.collection = MediaCollection(self.manager)
    
    def test_init(self):
        """Test MediaCollection initialization."""
        assert self.collection.manager == self.manager
    
    @patch('novus_pytils.globals.SUPPORTED_TEXT_EXTENSIONS', ['.txt'])
    def test_text_single_file(self):
        """Test getting single text file."""
        result = self.collection.text('test.txt')
        
        assert isinstance(result, File)
        assert result.path == 'test.txt'
        assert result.file_type == 'text'
    
    def test_text_single_file_wrong_type(self):
        """Test getting single file with wrong type."""
        with pytest.raises(UnsupportedFormatError):
            self.collection.text('test.unknown')
    
    @patch.object(FileBatch, 'filter_by_type')
    def test_text_multiple_files(self, mock_filter):
        """Test getting multiple text files."""
        mock_filter.return_value = FileBatch(['file1.txt'], self.manager)
        
        result = self.collection.text(['file1.txt', 'file2.jpg'])
        
        assert isinstance(result, FileBatch)
        mock_filter.assert_called_once_with('text')
    
    @patch('novus_pytils.globals.SUPPORTED_IMAGE_EXTENSIONS', ['.jpg'])
    def test_image_single_file(self):
        """Test getting single image file."""
        result = self.collection.image('test.jpg')
        
        assert isinstance(result, File)
        assert result.path == 'test.jpg'
        assert result.file_type == 'image'
    
    @patch('novus_pytils.globals.SUPPORTED_AUDIO_EXTENSIONS', ['.mp3'])
    def test_audio_single_file(self):
        """Test getting single audio file."""
        result = self.collection.audio('test.mp3')
        
        assert isinstance(result, File)
        assert result.path == 'test.mp3'
        assert result.file_type == 'audio'
    
    @patch('novus_pytils.globals.SUPPORTED_VIDEO_EXTENSIONS', ['.mp4'])
    def test_video_single_file(self):
        """Test getting single video file."""
        result = self.collection.video('test.mp4')
        
        assert isinstance(result, File)
        assert result.path == 'test.mp4'
        assert result.file_type == 'video'


class TestFileManagerMixin:
    """Test FileManagerMixin class."""
    
    def setup_method(self):
        """Setup test handler with mixin."""
        class TestHandlerWithMixin(BaseFileHandler, FileManagerMixin):
            def read(self, file_path, **kwargs):
                return "content"
            
            def write(self, file_path, content, **kwargs):
                return True
            
            def convert(self, input_path, output_path, target_format, **kwargs):
                return True
        
        self.handler = TestHandlerWithMixin()
    
    @patch('os.path.splitext')
    @patch('os.path.basename')
    @patch('os.path.join')
    def test_batch_convert_with_output_dir(self, mock_join, mock_basename, mock_splitext):
        """Test batch convert with output directory."""
        mock_splitext.return_value = ('file1', '.txt')
        mock_basename.return_value = 'file1.txt'
        mock_join.return_value = '/output/file1.pdf'
        
        result = self.handler.batch_convert(['file1.txt'], '.pdf', '/output')
        
        assert result == {'file1.txt': True}
    
    @patch('os.path.splitext')
    def test_batch_convert_without_output_dir(self, mock_splitext):
        """Test batch convert without output directory."""
        mock_splitext.return_value = ('file1', '.txt')
        
        result = self.handler.batch_convert(['file1.txt'], '.pdf')
        
        assert result == {'file1.txt': True}
    
    def test_batch_convert_with_exception(self):
        """Test batch convert with exception."""
        # Override convert to raise exception
        def failing_convert(*args, **kwargs):
            raise Exception("Conversion failed")
        
        self.handler.convert = failing_convert
        
        result = self.handler.batch_convert(['file1.txt'], '.pdf')
        
        assert result == {'file1.txt': False}
    
    def test_batch_operation_delete(self):
        """Test batch delete operation."""
        # Mock the delete method
        self.handler.delete = lambda x: True
        
        result = self.handler.batch_operation(['file1.txt'], 'delete')
        
        assert result == {'file1.txt': True}
    
    @patch('os.path.join')
    @patch('os.path.basename')
    def test_batch_operation_copy(self, mock_basename, mock_join):
        """Test batch copy operation."""
        mock_basename.return_value = 'file1.txt'
        mock_join.return_value = '/dest/file1.txt'
        
        # Mock the copy method
        self.handler.copy = lambda src, dest: True
        
        result = self.handler.batch_operation(['file1.txt'], 'copy', dest_dir='/dest')
        
        assert result == {'file1.txt': True}
    
    @patch('os.path.join')
    @patch('os.path.basename')
    def test_batch_operation_move(self, mock_basename, mock_join):
        """Test batch move operation."""
        mock_basename.return_value = 'file1.txt'
        mock_join.return_value = '/dest/file1.txt'
        
        # Mock the move method
        self.handler.move = lambda src, dest: True
        
        result = self.handler.batch_operation(['file1.txt'], 'move', dest_dir='/dest')
        
        assert result == {'file1.txt': True}
    
    def test_batch_operation_unknown(self):
        """Test batch operation with unknown operation."""
        result = self.handler.batch_operation(['file1.txt'], 'unknown')
        
        assert result == {'file1.txt': False}
    
    def test_batch_operation_with_exception(self):
        """Test batch operation with exception."""
        # Override delete to raise exception
        def failing_delete(*args, **kwargs):
            raise Exception("Delete failed")
        
        self.handler.delete = failing_delete
        
        result = self.handler.batch_operation(['file1.txt'], 'delete')
        
        assert result == {'file1.txt': False}


class TestValidationResult:
    """Test ValidationResult dataclass."""
    
    def test_init_valid(self):
        """Test ValidationResult initialization for valid result."""
        result = ValidationResult(is_valid=True, message="Valid")
        
        assert result.is_valid is True
        assert result.message == "Valid"
        assert result.errors == []
    
    def test_init_invalid(self):
        """Test ValidationResult initialization for invalid result."""
        result = ValidationResult(is_valid=False, message="Invalid", errors=["Error 1"])
        
        assert result.is_valid is False
        assert result.message == "Invalid"
        assert result.errors == ["Error 1"]
    
    def test_init_with_none_errors(self):
        """Test ValidationResult initialization with None errors."""
        result = ValidationResult(is_valid=True)
        
        assert result.errors == []
    
    def test_str_representation(self):
        """Test string representation."""
        result = ValidationResult(is_valid=True, message="Valid")
        
        assert str(result) == "ValidationResult(valid=True, message='Valid')"


class TestColorCode:
    """Test ColorCode enum."""
    
    def test_color_values(self):
        """Test color code values."""
        assert ColorCode.RED.value == '\033[91m'
        assert ColorCode.GREEN.value == '\033[92m'
        assert ColorCode.YELLOW.value == '\033[93m'
        assert ColorCode.BLUE.value == '\033[94m'
        assert ColorCode.MAGENTA.value == '\033[95m'
        assert ColorCode.CYAN.value == '\033[96m'
        assert ColorCode.WHITE.value == '\033[97m'
        assert ColorCode.BLACK.value == '\033[30m'
        assert ColorCode.RESET.value == '\033[0m'
        assert ColorCode.BOLD.value == '\033[1m'
        assert ColorCode.UNDERLINE.value == '\033[4m'
    
    def test_enum_membership(self):
        """Test enum membership."""
        assert ColorCode.RED in ColorCode
        assert ColorCode.GREEN in ColorCode
        assert ColorCode.RESET in ColorCode
    
    def test_enum_iteration(self):
        """Test enum iteration."""
        colors = list(ColorCode)
        assert len(colors) == 11
        assert ColorCode.RED in colors
        assert ColorCode.RESET in colors