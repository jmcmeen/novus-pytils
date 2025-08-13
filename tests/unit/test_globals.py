"""Unit tests for globals module."""
import pytest

from novus_pytils.globals import (
    SUPPORTED_TEXT_EXTENSIONS, SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS,
    DEFAULT_QUALITY, MAX_FILE_SIZE_MB, TEMP_DIRECTORY,
    API_HOST, API_PORT, get_all_supported_extensions,
    is_supported_extension, get_file_type_by_extension,
    get_default_conversion_quality, validate_file_type
)


class TestSupportedExtensions:
    """Test supported file extensions constants."""
    
    def test_text_extensions_exist(self):
        """Test that text extensions are defined."""
        assert isinstance(SUPPORTED_TEXT_EXTENSIONS, (list, tuple, set))
        assert len(SUPPORTED_TEXT_EXTENSIONS) > 0
        
        # Check some common text extensions
        expected_text_exts = ['.txt', '.md', '.csv', '.json', '.xml']
        for ext in expected_text_exts:
            assert ext in SUPPORTED_TEXT_EXTENSIONS
    
    def test_image_extensions_exist(self):
        """Test that image extensions are defined."""
        assert isinstance(SUPPORTED_IMAGE_EXTENSIONS, (list, tuple, set))
        assert len(SUPPORTED_IMAGE_EXTENSIONS) > 0
        
        # Check some common image extensions
        expected_image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        for ext in expected_image_exts:
            assert ext in SUPPORTED_IMAGE_EXTENSIONS
    
    def test_audio_extensions_exist(self):
        """Test that audio extensions are defined."""
        assert isinstance(SUPPORTED_AUDIO_EXTENSIONS, (list, tuple, set))
        assert len(SUPPORTED_AUDIO_EXTENSIONS) > 0
        
        # Check some common audio extensions
        expected_audio_exts = ['.mp3', '.wav', '.ogg', '.flac', '.aac']
        for ext in expected_audio_exts:
            assert ext in SUPPORTED_AUDIO_EXTENSIONS
    
    def test_video_extensions_exist(self):
        """Test that video extensions are defined."""
        assert isinstance(SUPPORTED_VIDEO_EXTENSIONS, (list, tuple, set))
        assert len(SUPPORTED_VIDEO_EXTENSIONS) > 0
        
        # Check some common video extensions
        expected_video_exts = ['.mp4', '.avi', '.mkv', '.mov', '.webm']
        for ext in expected_video_exts:
            assert ext in SUPPORTED_VIDEO_EXTENSIONS
    
    def test_extensions_are_lowercase(self):
        """Test that all extensions are in lowercase."""
        all_extensions = (
            list(SUPPORTED_TEXT_EXTENSIONS) +
            list(SUPPORTED_IMAGE_EXTENSIONS) +
            list(SUPPORTED_AUDIO_EXTENSIONS) +
            list(SUPPORTED_VIDEO_EXTENSIONS)
        )
        
        for ext in all_extensions:
            assert ext == ext.lower(), f"Extension {ext} should be lowercase"
    
    def test_extensions_start_with_dot(self):
        """Test that all extensions start with a dot."""
        all_extensions = (
            list(SUPPORTED_TEXT_EXTENSIONS) +
            list(SUPPORTED_IMAGE_EXTENSIONS) +
            list(SUPPORTED_AUDIO_EXTENSIONS) +
            list(SUPPORTED_VIDEO_EXTENSIONS)
        )
        
        for ext in all_extensions:
            assert ext.startswith('.'), f"Extension {ext} should start with a dot"
    
    def test_no_duplicate_extensions(self):
        """Test that there are no duplicate extensions across categories."""
        all_extensions = (
            list(SUPPORTED_TEXT_EXTENSIONS) +
            list(SUPPORTED_IMAGE_EXTENSIONS) +
            list(SUPPORTED_AUDIO_EXTENSIONS) +
            list(SUPPORTED_VIDEO_EXTENSIONS)
        )
        
        unique_extensions = set(all_extensions)
        assert len(all_extensions) == len(unique_extensions), "Found duplicate extensions"


class TestDefaultConstants:
    """Test default configuration constants."""
    
    def test_default_quality(self):
        """Test default quality constant."""
        assert isinstance(DEFAULT_QUALITY, int)
        assert 1 <= DEFAULT_QUALITY <= 100
    
    def test_max_file_size_mb(self):
        """Test max file size constant."""
        assert isinstance(MAX_FILE_SIZE_MB, (int, float))
        assert MAX_FILE_SIZE_MB > 0
    
    def test_temp_directory(self):
        """Test temp directory constant."""
        assert isinstance(TEMP_DIRECTORY, str)
        assert len(TEMP_DIRECTORY) > 0
    
    def test_api_host(self):
        """Test API host constant."""
        assert isinstance(API_HOST, str)
        assert len(API_HOST) > 0
    
    def test_api_port(self):
        """Test API port constant."""
        assert isinstance(API_PORT, int)
        assert 1 <= API_PORT <= 65535


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_all_supported_extensions(self):
        """Test get_all_supported_extensions function."""
        all_extensions = get_all_supported_extensions()
        
        assert isinstance(all_extensions, (list, set))
        assert len(all_extensions) > 0
        
        # Check that all category extensions are included
        for ext in SUPPORTED_TEXT_EXTENSIONS:
            assert ext in all_extensions
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            assert ext in all_extensions
        for ext in SUPPORTED_AUDIO_EXTENSIONS:
            assert ext in all_extensions
        for ext in SUPPORTED_VIDEO_EXTENSIONS:
            assert ext in all_extensions
    
    def test_get_all_supported_extensions_no_duplicates(self):
        """Test that get_all_supported_extensions returns no duplicates."""
        all_extensions = get_all_supported_extensions()
        
        if isinstance(all_extensions, list):
            unique_extensions = set(all_extensions)
            assert len(all_extensions) == len(unique_extensions)
    
    def test_is_supported_extension_text(self):
        """Test is_supported_extension for text files."""
        assert is_supported_extension('.txt') is True
        assert is_supported_extension('.TXT') is True  # Case insensitive
        assert is_supported_extension('txt') is True   # Without dot
    
    def test_is_supported_extension_image(self):
        """Test is_supported_extension for image files."""
        assert is_supported_extension('.jpg') is True
        assert is_supported_extension('.PNG') is True
        assert is_supported_extension('gif') is True
    
    def test_is_supported_extension_audio(self):
        """Test is_supported_extension for audio files."""
        assert is_supported_extension('.mp3') is True
        assert is_supported_extension('.WAV') is True
        assert is_supported_extension('ogg') is True
    
    def test_is_supported_extension_video(self):
        """Test is_supported_extension for video files."""
        assert is_supported_extension('.mp4') is True
        assert is_supported_extension('.AVI') is True
        assert is_supported_extension('mkv') is True
    
    def test_is_supported_extension_unsupported(self):
        """Test is_supported_extension for unsupported files."""
        assert is_supported_extension('.xyz') is False
        assert is_supported_extension('.unknown') is False
        assert is_supported_extension('') is False
    
    def test_get_file_type_by_extension_text(self):
        """Test get_file_type_by_extension for text files."""
        assert get_file_type_by_extension('.txt') == 'text'
        assert get_file_type_by_extension('.md') == 'text'
        assert get_file_type_by_extension('.csv') == 'text'
    
    def test_get_file_type_by_extension_image(self):
        """Test get_file_type_by_extension for image files."""
        assert get_file_type_by_extension('.jpg') == 'image'
        assert get_file_type_by_extension('.png') == 'image'
        assert get_file_type_by_extension('.gif') == 'image'
    
    def test_get_file_type_by_extension_audio(self):
        """Test get_file_type_by_extension for audio files."""
        assert get_file_type_by_extension('.mp3') == 'audio'
        assert get_file_type_by_extension('.wav') == 'audio'
        assert get_file_type_by_extension('.ogg') == 'audio'
    
    def test_get_file_type_by_extension_video(self):
        """Test get_file_type_by_extension for video files."""
        assert get_file_type_by_extension('.mp4') == 'video'
        assert get_file_type_by_extension('.avi') == 'video'
        assert get_file_type_by_extension('.mkv') == 'video'
    
    def test_get_file_type_by_extension_case_insensitive(self):
        """Test get_file_type_by_extension is case insensitive."""
        assert get_file_type_by_extension('.TXT') == 'text'
        assert get_file_type_by_extension('.JPG') == 'image'
        assert get_file_type_by_extension('.MP3') == 'audio'
        assert get_file_type_by_extension('.MP4') == 'video'
    
    def test_get_file_type_by_extension_with_filename(self):
        """Test get_file_type_by_extension with full filename."""
        assert get_file_type_by_extension('document.txt') == 'text'
        assert get_file_type_by_extension('photo.jpg') == 'image'
        assert get_file_type_by_extension('song.mp3') == 'audio'
        assert get_file_type_by_extension('movie.mp4') == 'video'
    
    def test_get_file_type_by_extension_unknown(self):
        """Test get_file_type_by_extension for unknown extensions."""
        assert get_file_type_by_extension('.xyz') == 'unknown'
        assert get_file_type_by_extension('.unknown') == 'unknown'
        assert get_file_type_by_extension('') == 'unknown'
    
    def test_get_default_conversion_quality_by_type(self):
        """Test get_default_conversion_quality for different file types."""
        # Test that function returns reasonable quality values
        text_quality = get_default_conversion_quality('text')
        assert isinstance(text_quality, int)
        assert 1 <= text_quality <= 100
        
        image_quality = get_default_conversion_quality('image')
        assert isinstance(image_quality, int)
        assert 1 <= image_quality <= 100
        
        audio_quality = get_default_conversion_quality('audio')
        assert isinstance(audio_quality, int)
        assert 1 <= audio_quality <= 100
        
        video_quality = get_default_conversion_quality('video')
        assert isinstance(video_quality, int)
        assert 1 <= video_quality <= 100
    
    def test_get_default_conversion_quality_unknown_type(self):
        """Test get_default_conversion_quality for unknown file type."""
        default_quality = get_default_conversion_quality('unknown')
        assert default_quality == DEFAULT_QUALITY
    
    def test_validate_file_type_valid_types(self):
        """Test validate_file_type for valid file types."""
        assert validate_file_type('text') is True
        assert validate_file_type('image') is True
        assert validate_file_type('audio') is True
        assert validate_file_type('video') is True
    
    def test_validate_file_type_case_insensitive(self):
        """Test validate_file_type is case insensitive."""
        assert validate_file_type('TEXT') is True
        assert validate_file_type('Image') is True
        assert validate_file_type('AUDIO') is True
        assert validate_file_type('Video') is True
    
    def test_validate_file_type_invalid(self):
        """Test validate_file_type for invalid file types."""
        assert validate_file_type('invalid') is False
        assert validate_file_type('unknown') is False
        assert validate_file_type('') is False
        assert validate_file_type(None) is False


class TestExtensionMapping:
    """Test extension to type mapping consistency."""
    
    def test_extension_mapping_completeness(self):
        """Test that all extensions can be mapped to a type."""
        all_extensions = get_all_supported_extensions()
        
        for ext in all_extensions:
            file_type = get_file_type_by_extension(ext)
            assert file_type in ['text', 'image', 'audio', 'video'], \
                f"Extension {ext} mapped to unknown type: {file_type}"
    
    def test_extension_mapping_consistency(self):
        """Test that extension mapping is consistent."""
        # Test that extensions in each category map to correct type
        for ext in SUPPORTED_TEXT_EXTENSIONS:
            assert get_file_type_by_extension(ext) == 'text'
        
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            assert get_file_type_by_extension(ext) == 'image'
        
        for ext in SUPPORTED_AUDIO_EXTENSIONS:
            assert get_file_type_by_extension(ext) == 'audio'
        
        for ext in SUPPORTED_VIDEO_EXTENSIONS:
            assert get_file_type_by_extension(ext) == 'video'


class TestConfigurationValidation:
    """Test configuration validation."""
    
    def test_quality_values_in_range(self):
        """Test that all quality values are in valid range."""
        for file_type in ['text', 'image', 'audio', 'video']:
            quality = get_default_conversion_quality(file_type)
            assert 1 <= quality <= 100, \
                f"Quality for {file_type} is out of range: {quality}"
    
    def test_file_size_reasonable(self):
        """Test that max file size is reasonable."""
        # Max file size should be at least 1MB and not more than 10GB
        assert 1 <= MAX_FILE_SIZE_MB <= 10000
    
    def test_api_configuration_valid(self):
        """Test that API configuration is valid."""
        # Host should not be empty
        assert len(API_HOST.strip()) > 0
        
        # Port should be in valid range
        assert 1 <= API_PORT <= 65535
        
        # Common ports check
        assert API_PORT not in [22, 23, 25, 53, 110, 143, 993, 995], \
            "API port conflicts with common service ports"


class TestMemoryEfficiency:
    """Test memory efficiency of globals."""
    
    def test_extensions_are_immutable(self):
        """Test that extension collections are immutable or can be made immutable."""
        # This test ensures that the extension collections don't accidentally get modified
        original_text_count = len(SUPPORTED_TEXT_EXTENSIONS)
        original_image_count = len(SUPPORTED_IMAGE_EXTENSIONS)
        original_audio_count = len(SUPPORTED_AUDIO_EXTENSIONS)
        original_video_count = len(SUPPORTED_VIDEO_EXTENSIONS)
        
        # Try to call functions that might modify the collections
        get_all_supported_extensions()
        is_supported_extension('.txt')
        get_file_type_by_extension('.jpg')
        
        # Verify counts haven't changed
        assert len(SUPPORTED_TEXT_EXTENSIONS) == original_text_count
        assert len(SUPPORTED_IMAGE_EXTENSIONS) == original_image_count
        assert len(SUPPORTED_AUDIO_EXTENSIONS) == original_audio_count
        assert len(SUPPORTED_VIDEO_EXTENSIONS) == original_video_count
    
    def test_function_calls_are_efficient(self):
        """Test that function calls don't create excessive objects."""
        import sys
        
        # Get initial object count
        initial_objects = len(gc.get_objects()) if 'gc' in sys.modules else 0
        
        # Call functions multiple times
        for _ in range(100):
            get_all_supported_extensions()
            is_supported_extension('.txt')
            get_file_type_by_extension('.jpg')
            get_default_conversion_quality('image')
        
        # Object count shouldn't grow excessively
        if 'gc' in sys.modules:
            import gc
            final_objects = len(gc.get_objects())
            # Allow some growth but not excessive
            assert final_objects - initial_objects < 1000