"""Unit tests for api.functional module."""
import pytest
from unittest.mock import patch, MagicMock

from novus_pytils.files import (
    _get_handler, read_file, write_file, create_file, update_file,
    delete_file, copy_file, move_file, convert_file, get_file_info,
    get_supported_conversions, batch_convert, batch_operation,
    resize_image, crop_image, trim_audio, trim_video, merge_files,
    split_file, create_thumbnail, apply_filter, extract_audio_from_video,
    extract_frames_from_video, normalize_audio, change_audio_volume
)
from novus_pytils.exceptions import UnsupportedFormatError


class TestGetHandler:
    """Test _get_handler function."""
    
    @patch('novus_pytils.globals.SUPPORTED_TEXT_EXTENSIONS', ['.txt', '.md'])
    def test_get_handler_text(self):
        """Test getting text handler."""
        handler, file_type = _get_handler('test.txt')
        assert file_type == 'text'
        
    @patch('novus_pytils.globals.SUPPORTED_IMAGE_EXTENSIONS', ['.jpg', '.png'])
    def test_get_handler_image(self):
        """Test getting image handler."""
        handler, file_type = _get_handler('test.jpg')
        assert file_type == 'image'
        
    @patch('novus_pytils.globals.SUPPORTED_AUDIO_EXTENSIONS', ['.mp3', '.wav'])
    def test_get_handler_audio(self):
        """Test getting audio handler."""
        handler, file_type = _get_handler('test.mp3')
        assert file_type == 'audio'
        
    @patch('novus_pytils.globals.SUPPORTED_VIDEO_EXTENSIONS', ['.mp4', '.avi'])
    def test_get_handler_video(self):
        """Test getting video handler."""
        handler, file_type = _get_handler('test.mp4')
        assert file_type == 'video'
        
    def test_get_handler_unsupported(self):
        """Test getting handler for unsupported format."""
        with pytest.raises(UnsupportedFormatError):
            _get_handler('test.unknown')


class TestBasicFileOperations:
    """Test basic file operations."""
    
    @patch('novus_pytils.files._get_handler')
    def test_read_file(self, mock_get_handler):
        """Test reading a file."""
        mock_handler = MagicMock()
        mock_handler.read.return_value = "test content"
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = read_file('test.txt')
        
        assert result == "test content"
        mock_handler.read.assert_called_once_with('test.txt')
        
    @patch('novus_pytils.files._get_handler')
    def test_write_file(self, mock_get_handler):
        """Test writing a file."""
        mock_handler = MagicMock()
        mock_handler.write.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = write_file('test.txt', 'content')
        
        assert result is True
        mock_handler.write.assert_called_once_with('test.txt', 'content')
        
    @patch('novus_pytils.files._get_handler')
    def test_create_file(self, mock_get_handler):
        """Test creating a file."""
        mock_handler = MagicMock()
        mock_handler.create.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = create_file('test.txt', 'content')
        
        assert result is True
        mock_handler.create.assert_called_once_with('test.txt', 'content')
        
    @patch('novus_pytils.files._get_handler')
    def test_update_file(self, mock_get_handler):
        """Test updating a file."""
        mock_handler = MagicMock()
        mock_handler.update.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = update_file('test.txt', 'new content')
        
        assert result is True
        mock_handler.update.assert_called_once_with('test.txt', 'new content')
        
    @patch('novus_pytils.files._get_handler')
    def test_delete_file(self, mock_get_handler):
        """Test deleting a file."""
        mock_handler = MagicMock()
        mock_handler.delete.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = delete_file('test.txt')
        
        assert result is True
        mock_handler.delete.assert_called_once_with('test.txt')
        
    @patch('novus_pytils.files._get_handler')
    def test_copy_file(self, mock_get_handler):
        """Test copying a file."""
        mock_handler = MagicMock()
        mock_handler.copy.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = copy_file('src.txt', 'dest.txt')
        
        assert result is True
        mock_handler.copy.assert_called_once_with('src.txt', 'dest.txt')
        
    @patch('novus_pytils.files._get_handler')
    def test_move_file(self, mock_get_handler):
        """Test moving a file."""
        mock_handler = MagicMock()
        mock_handler.move.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = move_file('src.txt', 'dest.txt')
        
        assert result is True
        mock_handler.move.assert_called_once_with('src.txt', 'dest.txt')
        
    @patch('novus_pytils.files._get_handler')
    def test_convert_file(self, mock_get_handler):
        """Test converting a file."""
        mock_handler = MagicMock()
        mock_handler.convert.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        
        result = convert_file('input.jpg', 'output.png', '.png')
        
        assert result is True
        mock_handler.convert.assert_called_once_with('input.jpg', 'output.png', '.png')


class TestFileInfo:
    """Test file information operations."""
    
    @patch('novus_pytils.files._get_handler')
    def test_get_file_info_image(self, mock_get_handler):
        """Test getting image file info."""
        mock_handler = MagicMock()
        mock_handler.get_image_info.return_value = {'width': 100, 'height': 100}
        mock_get_handler.return_value = (mock_handler, 'image')
        
        result = get_file_info('test.jpg')
        
        assert result == {'width': 100, 'height': 100}
        mock_handler.get_image_info.assert_called_once_with('test.jpg')
        
    @patch('novus_pytils.files._get_handler')
    def test_get_file_info_audio(self, mock_get_handler):
        """Test getting audio file info."""
        mock_handler = MagicMock()
        mock_handler.get_audio_info.return_value = {'duration': 120, 'bitrate': 320}
        mock_get_handler.return_value = (mock_handler, 'audio')
        
        result = get_file_info('test.mp3')
        
        assert result == {'duration': 120, 'bitrate': 320}
        mock_handler.get_audio_info.assert_called_once_with('test.mp3')
        
    @patch('novus_pytils.files._get_handler')
    def test_get_file_info_video(self, mock_get_handler):
        """Test getting video file info."""
        mock_handler = MagicMock()
        mock_handler.get_video_info.return_value = {'duration': 300, 'fps': 30}
        mock_get_handler.return_value = (mock_handler, 'video')
        
        result = get_file_info('test.mp4')
        
        assert result == {'duration': 300, 'fps': 30}
        mock_handler.get_video_info.assert_called_once_with('test.mp4')
        
    @patch('novus_pytils.files._get_handler')
    def test_get_file_info_fallback(self, mock_get_handler):
        """Test getting file info fallback to metadata."""
        mock_handler = MagicMock()
        mock_handler.get_metadata.return_value = {'size': 1024}
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = get_file_info('test.txt')
        
        assert result == {'size': 1024}
        mock_handler.get_metadata.assert_called_once_with('test.txt')
        
    @patch('novus_pytils.files._get_handler')
    def test_get_supported_conversions(self, mock_get_handler):
        """Test getting supported conversions."""
        mock_handler = MagicMock()
        mock_handler.get_supported_conversions.return_value = ['.png', '.gif']
        mock_get_handler.return_value = (mock_handler, 'image')
        
        result = get_supported_conversions('test.jpg')
        
        assert result == ['.png', '.gif']
        mock_handler.get_supported_conversions.assert_called_once_with('.jpg')


class TestBatchOperations:
    """Test batch operations."""
    
    @patch('novus_pytils.files._get_handler')
    def test_batch_convert_with_batch_support(self, mock_get_handler):
        """Test batch convert with handler that supports batch operations."""
        mock_handler = MagicMock()
        mock_handler.batch_convert.return_value = {'file1.jpg': True, 'file2.jpg': True}
        mock_get_handler.return_value = (mock_handler, 'image')
        
        result = batch_convert(['file1.jpg', 'file2.jpg'], '.png')
        
        assert result == {'file1.jpg': True, 'file2.jpg': True}
        
    @patch('novus_pytils.files._get_handler')
    @patch('os.path.splitext')
    def test_batch_convert_without_batch_support(self, mock_splitext, mock_get_handler):
        """Test batch convert with handler that doesn't support batch operations."""
        mock_handler = MagicMock()
        # Remove batch_convert method to simulate handler without batch support
        del mock_handler.batch_convert
        mock_handler.convert.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        mock_splitext.return_value = ('file1', '.jpg')
        
        result = batch_convert(['file1.jpg'], '.png')
        
        assert result == {'file1.jpg': True}
        
    @patch('novus_pytils.files._get_handler')
    def test_batch_convert_with_exception(self, mock_get_handler):
        """Test batch convert with exception."""
        mock_get_handler.side_effect = Exception("Error")
        
        result = batch_convert(['file1.jpg'], '.png')
        
        assert result == {'file1.jpg': False}
        
    @patch('novus_pytils.files._get_handler')
    def test_batch_operation_delete(self, mock_get_handler):
        """Test batch delete operation."""
        mock_handler = MagicMock()
        mock_handler.delete.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = batch_operation(['file1.txt'], 'delete')
        
        assert result == {'file1.txt': True}
        
    @patch('novus_pytils.files._get_handler')
    @patch('os.path.basename')
    @patch('os.path.join')
    def test_batch_operation_copy(self, mock_join, mock_basename, mock_get_handler):
        """Test batch copy operation."""
        mock_handler = MagicMock()
        mock_handler.copy.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        mock_basename.return_value = 'file1.txt'
        mock_join.return_value = '/dest/file1.txt'
        
        result = batch_operation(['file1.txt'], 'copy', dest_dir='/dest')
        
        assert result == {'file1.txt': True}
        
    @patch('novus_pytils.files.get_file_info')
    @patch('novus_pytils.files._get_handler')
    def test_batch_operation_info(self, mock_get_handler, mock_get_info):
        """Test batch info operation."""
        mock_handler = MagicMock()
        mock_get_handler.return_value = (mock_handler, 'text')
        mock_get_info.return_value = {'size': 1024}
        
        result = batch_operation(['file1.txt'], 'info')
        
        assert result == {'file1.txt': {'size': 1024}}


class TestImageOperations:
    """Test image-specific operations."""
    
    @patch('novus_pytils.files._get_handler')
    def test_resize_image(self, mock_get_handler):
        """Test resizing an image."""
        mock_handler = MagicMock()
        mock_handler.resize.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        
        result = resize_image('input.jpg', 'output.jpg', (100, 100))
        
        assert result is True
        mock_handler.resize.assert_called_once_with('input.jpg', 'output.jpg', (100, 100), True)
        
    @patch('novus_pytils.files._get_handler')
    def test_resize_image_not_image(self, mock_get_handler):
        """Test resizing non-image file."""
        mock_get_handler.return_value = (MagicMock(), 'text')
        
        with pytest.raises(UnsupportedFormatError):
            resize_image('input.txt', 'output.txt', (100, 100))
            
    @patch('novus_pytils.files._get_handler')
    def test_crop_image(self, mock_get_handler):
        """Test cropping an image."""
        mock_handler = MagicMock()
        mock_handler.crop.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        
        result = crop_image('input.jpg', 'output.jpg', (0, 0, 100, 100))
        
        assert result is True
        mock_handler.crop.assert_called_once_with('input.jpg', 'output.jpg', (0, 0, 100, 100))


class TestAudioOperations:
    """Test audio-specific operations."""
    
    @patch('novus_pytils.files._get_handler')
    def test_trim_audio(self, mock_get_handler):
        """Test trimming audio."""
        mock_handler = MagicMock()
        mock_handler.trim.return_value = True
        mock_get_handler.return_value = (mock_handler, 'audio')
        
        result = trim_audio('input.mp3', 'output.mp3', 1000, 5000)
        
        assert result is True
        mock_handler.trim.assert_called_once_with('input.mp3', 'output.mp3', 1000, 5000)
        
    @patch('novus_pytils.files._get_handler')
    def test_trim_audio_not_audio(self, mock_get_handler):
        """Test trimming non-audio file."""
        mock_get_handler.return_value = (MagicMock(), 'text')
        
        with pytest.raises(UnsupportedFormatError):
            trim_audio('input.txt', 'output.txt', 1000, 5000)
            
    @patch('novus_pytils.files._get_handler')
    def test_normalize_audio(self, mock_get_handler):
        """Test normalizing audio."""
        mock_handler = MagicMock()
        mock_handler.normalize.return_value = True
        mock_get_handler.return_value = (mock_handler, 'audio')
        
        result = normalize_audio('input.mp3', 'output.mp3', -15.0)
        
        assert result is True
        mock_handler.normalize.assert_called_once_with('input.mp3', 'output.mp3', -15.0)
        
    @patch('novus_pytils.files._get_handler')
    def test_change_audio_volume(self, mock_get_handler):
        """Test changing audio volume."""
        mock_handler = MagicMock()
        mock_handler.change_volume.return_value = True
        mock_get_handler.return_value = (mock_handler, 'audio')
        
        result = change_audio_volume('input.mp3', 'output.mp3', 5.0)
        
        assert result is True
        mock_handler.change_volume.assert_called_once_with('input.mp3', 'output.mp3', 5.0)


class TestVideoOperations:
    """Test video-specific operations."""
    
    @patch('novus_pytils.files._get_handler')
    def test_trim_video(self, mock_get_handler):
        """Test trimming video."""
        mock_handler = MagicMock()
        mock_handler.trim.return_value = True
        mock_get_handler.return_value = (mock_handler, 'video')
        
        result = trim_video('input.mp4', 'output.mp4', '00:01:00', duration='00:02:00')
        
        assert result is True
        mock_handler.trim.assert_called_once_with('input.mp4', 'output.mp4', '00:01:00', '00:02:00', None)
        
    @patch('novus_pytils.files._get_handler')
    def test_extract_audio_from_video(self, mock_get_handler):
        """Test extracting audio from video."""
        mock_handler = MagicMock()
        mock_handler.extract_audio.return_value = True
        mock_get_handler.return_value = (mock_handler, 'video')
        
        result = extract_audio_from_video('input.mp4', 'output.mp3')
        
        assert result is True
        mock_handler.extract_audio.assert_called_once_with('input.mp4', 'output.mp3')
        
    @patch('novus_pytils.files._get_handler')
    def test_extract_frames_from_video(self, mock_get_handler):
        """Test extracting frames from video."""
        mock_handler = MagicMock()
        mock_handler.extract_frames.return_value = ['frame1.jpg', 'frame2.jpg']
        mock_get_handler.return_value = (mock_handler, 'video')
        
        result = extract_frames_from_video('input.mp4', '/output', 2.0)
        
        assert result == ['frame1.jpg', 'frame2.jpg']
        mock_handler.extract_frames.assert_called_once_with('input.mp4', '/output', 2.0)


class TestMergeAndSplit:
    """Test merge and split operations."""
    
    @patch('novus_pytils.files._get_handler')
    def test_merge_files_text(self, mock_get_handler):
        """Test merging text files."""
        mock_handler = MagicMock()
        mock_handler.merge_files.return_value = True
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = merge_files(['file1.txt', 'file2.txt'], 'output.txt', separator=' ')
        
        assert result is True
        mock_handler.merge_files.assert_called_once_with(['file1.txt', 'file2.txt'], 'output.txt', ' ')
        
    @patch('novus_pytils.files._get_handler')
    def test_merge_files_audio(self, mock_get_handler):
        """Test merging audio files."""
        mock_handler = MagicMock()
        mock_handler.concatenate.return_value = True
        mock_get_handler.return_value = (mock_handler, 'audio')
        
        result = merge_files(['file1.mp3', 'file2.mp3'], 'output.mp3')
        
        assert result is True
        mock_handler.concatenate.assert_called_once_with(['file1.mp3', 'file2.mp3'], 'output.mp3')
        
    @patch('novus_pytils.files._get_handler')
    def test_merge_files_unsupported(self, mock_get_handler):
        """Test merging unsupported file type."""
        mock_handler = MagicMock()
        # Remove merge_files method to simulate unsupported file type
        del mock_handler.merge_files
        mock_get_handler.return_value = (mock_handler, 'text')
        
        with pytest.raises(UnsupportedFormatError):
            merge_files(['file1.txt'], 'output.txt')
            
    def test_merge_files_empty_list(self):
        """Test merging empty file list."""
        result = merge_files([], 'output.txt')
        assert result is False
        
    @patch('novus_pytils.files._get_handler')
    def test_split_file_text(self, mock_get_handler):
        """Test splitting text file."""
        mock_handler = MagicMock()
        mock_handler.split_file.return_value = ['part1.txt', 'part2.txt']
        mock_get_handler.return_value = (mock_handler, 'text')
        
        result = split_file('input.txt', '/output', lines_per_file=500)
        
        assert result == ['part1.txt', 'part2.txt']
        mock_handler.split_file.assert_called_once_with('input.txt', '/output', 500)
        
    @patch('novus_pytils.files._get_handler')
    def test_split_file_audio(self, mock_get_handler):
        """Test splitting audio file."""
        mock_handler = MagicMock()
        mock_handler.split_on_silence.return_value = ['part1.mp3', 'part2.mp3']
        mock_get_handler.return_value = (mock_handler, 'audio')
        
        result = split_file('input.mp3', '/output', min_silence_len=2000)
        
        assert result == ['part1.mp3', 'part2.mp3']
        mock_handler.split_on_silence.assert_called_once_with('input.mp3', '/output', 2000, -40, min_silence_len=2000)


class TestThumbnailAndFilter:
    """Test thumbnail and filter operations."""
    
    @patch('novus_pytils.files._get_handler')
    def test_create_thumbnail_image(self, mock_get_handler):
        """Test creating thumbnail from image."""
        mock_handler = MagicMock()
        mock_handler.create_thumbnail.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        
        result = create_thumbnail('input.jpg', 'thumb.jpg', size=(64, 64))
        
        assert result is True
        mock_handler.create_thumbnail.assert_called_once_with('input.jpg', 'thumb.jpg', (64, 64), size=(64, 64))
        
    @patch('novus_pytils.files._get_handler')
    def test_create_thumbnail_video(self, mock_get_handler):
        """Test creating thumbnail from video."""
        mock_handler = MagicMock()
        mock_handler.create_thumbnail.return_value = True
        mock_get_handler.return_value = (mock_handler, 'video')
        
        result = create_thumbnail('input.mp4', 'thumb.jpg', time_position='00:00:05')
        
        assert result is True
        mock_handler.create_thumbnail.assert_called_once_with('input.mp4', 'thumb.jpg', '00:00:05', time_position='00:00:05')
        
    @patch('novus_pytils.files._get_handler')
    def test_apply_filter(self, mock_get_handler):
        """Test applying filter."""
        mock_handler = MagicMock()
        mock_handler.apply_filter.return_value = True
        mock_get_handler.return_value = (mock_handler, 'image')
        
        result = apply_filter('input.jpg', 'output.jpg', 'blur')
        
        assert result is True
        mock_handler.apply_filter.assert_called_once_with('input.jpg', 'output.jpg', 'blur')
        
    @patch('novus_pytils.files._get_handler')
    def test_apply_filter_unsupported(self, mock_get_handler):
        """Test applying filter to unsupported file type."""
        mock_handler = MagicMock()
        mock_get_handler.return_value = (mock_handler, 'text')
        
        with pytest.raises(UnsupportedFormatError):
            apply_filter('input.txt', 'output.txt', 'blur')