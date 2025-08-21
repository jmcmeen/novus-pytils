"""Unit tests for globals module."""
import gc

from novus_pytils.globals import (
    SUPPORTED_TEXT_EXTENSIONS, SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS,
    SUPPORTED_COMPRESSION_EXTENSIONS, ZIP_EXTS,
    WAVE_EXTS, OGG_EXTS, FLAC_EXTS, MP3_EXTS, AAC_EXTS, WMA_EXTS, M4A_EXTS,
    TXT_EXTS, MD_EXTS, CSV_EXTS, JSON_EXTS, XML_EXTS, LOG_EXTS, INI_EXTS, CFG_EXTS, YAML_EXTS,
    AVI_EXTS, MKV_EXTS, MP4_EXTS, MOV_EXTS, WMV_EXTS, FLV_EXTS, WEBM_EXTS, M4V_EXTS,
    JPG_EXTS, PNG_EXTS, GIF_EXTS, BMP_EXTS, TIFF_EXTS, WEBP_EXTS, SVG_EXTS,
    AUDIO_CONVERSION_MAP, VIDEO_CONVERSION_MAP, IMAGE_CONVERSION_MAP, TEXT_CONVERSION_MAP,
    get_all_supported_extensions, is_supported_extension, 
    get_file_type_by_extension, validate_file_type
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
    
    def test_compression_extensions_exist(self):
        """Test that compression extensions are defined."""
        assert isinstance(SUPPORTED_COMPRESSION_EXTENSIONS, (list, tuple, set))
        assert len(SUPPORTED_COMPRESSION_EXTENSIONS) > 0
        
        # Check zip extensions
        assert '.zip' in SUPPORTED_COMPRESSION_EXTENSIONS
    
    def test_extensions_are_lowercase(self):
        """Test that all extensions are in lowercase."""
        all_extensions = (
            list(SUPPORTED_TEXT_EXTENSIONS) +
            list(SUPPORTED_IMAGE_EXTENSIONS) +
            list(SUPPORTED_AUDIO_EXTENSIONS) +
            list(SUPPORTED_VIDEO_EXTENSIONS) +
            list(SUPPORTED_COMPRESSION_EXTENSIONS)
        )
        
        for ext in all_extensions:
            assert ext == ext.lower(), f"Extension {ext} should be lowercase"
    
    def test_extensions_start_with_dot(self):
        """Test that all extensions start with a dot."""
        all_extensions = (
            list(SUPPORTED_TEXT_EXTENSIONS) +
            list(SUPPORTED_IMAGE_EXTENSIONS) +
            list(SUPPORTED_AUDIO_EXTENSIONS) +
            list(SUPPORTED_VIDEO_EXTENSIONS) +
            list(SUPPORTED_COMPRESSION_EXTENSIONS)
        )
        
        for ext in all_extensions:
            assert ext.startswith('.'), f"Extension {ext} should start with a dot"
    
    def test_no_duplicate_extensions(self):
        """Test that there are no duplicate extensions across categories."""
        all_extensions = (
            list(SUPPORTED_TEXT_EXTENSIONS) +
            list(SUPPORTED_IMAGE_EXTENSIONS) +
            list(SUPPORTED_AUDIO_EXTENSIONS) +
            list(SUPPORTED_VIDEO_EXTENSIONS) +
            list(SUPPORTED_COMPRESSION_EXTENSIONS)
        )
        
        unique_extensions = set(all_extensions)
        assert len(all_extensions) == len(unique_extensions), "Found duplicate extensions"

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
        for ext in SUPPORTED_COMPRESSION_EXTENSIONS:
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
        assert is_supported_extension('.md') is True
    
    def test_is_supported_extension_image(self):
        """Test is_supported_extension for image files."""
        assert is_supported_extension('.jpg') is True
        assert is_supported_extension('.PNG') is True
        assert is_supported_extension('.gif') is True
    
    def test_is_supported_extension_audio(self):
        """Test is_supported_extension for audio files."""
        assert is_supported_extension('.mp3') is True
        assert is_supported_extension('.WAV') is True
        assert is_supported_extension('.ogg') is True
    
    def test_is_supported_extension_video(self):
        """Test is_supported_extension for video files."""
        assert is_supported_extension('.mp4') is True
        assert is_supported_extension('.AVI') is True
        assert is_supported_extension('.mkv') is True
    
    def test_is_supported_extension_compression(self):
        """Test is_supported_extension for compression files."""
        assert is_supported_extension('.zip') is True
        assert is_supported_extension('.ZIP') is True
    
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
    
    def test_get_file_type_by_extension_compression(self):
        """Test get_file_type_by_extension for compression files."""
        # Note: Currently compression files return 'unknown' since get_file_type_by_extension 
        # doesn't have a case for compression extensions
        assert get_file_type_by_extension('.zip') == 'unknown'
        assert get_file_type_by_extension('.ZIP') == 'unknown'
    
    def test_get_file_type_by_extension_with_filename(self):
        """Test get_file_type_by_extension with different extensions."""
        assert get_file_type_by_extension('.csv') == 'text'
        assert get_file_type_by_extension('.png') == 'image'
        assert get_file_type_by_extension('.wav') == 'audio'
        assert get_file_type_by_extension('.avi') == 'video'
    
    def test_get_file_type_by_extension_unknown(self):
        """Test get_file_type_by_extension for unknown extensions."""
        assert get_file_type_by_extension('.xyz') == 'unknown'
        assert get_file_type_by_extension('.unknown') == 'unknown'
        assert get_file_type_by_extension('') == 'unknown'
    
    def test_validate_file_type_valid_types(self):
        """Test validate_file_type for valid file types."""
        assert validate_file_type('file.txt') is True
        assert validate_file_type('image.jpg') is True
        assert validate_file_type('audio.mp3') is True
        assert validate_file_type('video.mp4') is True
    
    def test_validate_file_type_case_insensitive(self):
        """Test validate_file_type is case insensitive."""
        assert validate_file_type('file.TXT') is True
        assert validate_file_type('Image.JPG') is True
        assert validate_file_type('AUDIO.MP3') is True
        assert validate_file_type('Video.MP4') is True
    
    def test_validate_file_type_invalid(self):
        """Test validate_file_type for invalid file types."""
        assert validate_file_type('file.invalid') is False
        assert validate_file_type('file.unknown') is False
        assert validate_file_type('') is False
        # Note: None will cause TypeError, so we'll skip that test


class TestExtensionMapping:
    """Test extension to type mapping consistency."""
    
    def test_extension_mapping_completeness(self):
        """Test that all extensions can be mapped to a type."""
        all_extensions = get_all_supported_extensions()
        
        for ext in all_extensions:
            file_type = get_file_type_by_extension(ext)
            # Note: compression files currently return 'unknown' 
            assert file_type in ['text', 'image', 'audio', 'video', 'unknown'], \
                f"Extension {ext} mapped to unexpected type: {file_type}"
    
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
        
        # Note: compression extensions currently return 'unknown'
        for ext in SUPPORTED_COMPRESSION_EXTENSIONS:
            assert get_file_type_by_extension(ext) == 'unknown'


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
        
        # Get initial object count
        initial_objects = len(gc.get_objects())
        
        # Call functions multiple times
        for _ in range(100):
            get_all_supported_extensions()
            is_supported_extension('.txt')
            get_file_type_by_extension('.jpg')
        
        # Object count shouldn't grow excessively
        final_objects = len(gc.get_objects())
        # Allow some growth but not excessive
        assert final_objects - initial_objects < 1000


class TestIndividualExtensionConstants:
    """Test individual extension constants."""
    
    def test_audio_extension_constants(self):
        """Test individual audio extension constants."""
        assert WAVE_EXTS == ['.wav']
        assert OGG_EXTS == ['.ogg']
        assert FLAC_EXTS == ['.flac']
        assert MP3_EXTS == ['.mp3']
        assert AAC_EXTS == ['.aac']
        assert WMA_EXTS == ['.wma']
        assert M4A_EXTS == ['.m4a']
        
        # Verify they combine to form SUPPORTED_AUDIO_EXTENSIONS
        combined_audio = WAVE_EXTS + OGG_EXTS + FLAC_EXTS + MP3_EXTS + AAC_EXTS + WMA_EXTS + M4A_EXTS
        assert set(combined_audio) == set(SUPPORTED_AUDIO_EXTENSIONS)
    
    def test_text_extension_constants(self):
        """Test individual text extension constants."""
        assert TXT_EXTS == ['.txt']
        assert '.md' in MD_EXTS and '.markdown' in MD_EXTS
        assert CSV_EXTS == ['.csv']
        assert JSON_EXTS == ['.json']
        assert XML_EXTS == ['.xml']
        assert LOG_EXTS == ['.log']
        assert INI_EXTS == ['.ini']
        assert '.cfg' in CFG_EXTS and '.conf' in CFG_EXTS
        assert '.yaml' in YAML_EXTS and '.yml' in YAML_EXTS
        
        # Verify they combine to form SUPPORTED_TEXT_EXTENSIONS
        combined_text = TXT_EXTS + MD_EXTS + CSV_EXTS + JSON_EXTS + XML_EXTS + LOG_EXTS + INI_EXTS + CFG_EXTS + YAML_EXTS
        assert set(combined_text) == set(SUPPORTED_TEXT_EXTENSIONS)
    
    def test_video_extension_constants(self):
        """Test individual video extension constants."""
        assert AVI_EXTS == ['.avi']
        assert MKV_EXTS == ['.mkv']
        assert MP4_EXTS == ['.mp4']
        assert MOV_EXTS == ['.mov']
        assert WMV_EXTS == ['.wmv']
        assert FLV_EXTS == ['.flv']
        assert WEBM_EXTS == ['.webm']
        assert M4V_EXTS == ['.m4v']
        
        # Verify they combine to form SUPPORTED_VIDEO_EXTENSIONS
        combined_video = AVI_EXTS + MKV_EXTS + MP4_EXTS + MOV_EXTS + WMV_EXTS + FLV_EXTS + WEBM_EXTS + M4V_EXTS
        assert set(combined_video) == set(SUPPORTED_VIDEO_EXTENSIONS)
    
    def test_image_extension_constants(self):
        """Test individual image extension constants."""
        assert '.jpg' in JPG_EXTS and '.jpeg' in JPG_EXTS
        assert PNG_EXTS == ['.png']
        assert GIF_EXTS == ['.gif']
        assert BMP_EXTS == ['.bmp']
        assert '.tiff' in TIFF_EXTS and '.tif' in TIFF_EXTS
        assert WEBP_EXTS == ['.webp']
        assert SVG_EXTS == ['.svg']
        
        # Verify they combine to form SUPPORTED_IMAGE_EXTENSIONS
        combined_image = JPG_EXTS + PNG_EXTS + GIF_EXTS + BMP_EXTS + TIFF_EXTS + WEBP_EXTS + SVG_EXTS
        assert set(combined_image) == set(SUPPORTED_IMAGE_EXTENSIONS)
    
    def test_compression_extension_constants(self):
        """Test compression extension constants."""
        assert ZIP_EXTS == ['.zip']
        assert set(ZIP_EXTS) == set(SUPPORTED_COMPRESSION_EXTENSIONS)


class TestConversionMaps:
    """Test conversion mapping constants."""
    
    def test_audio_conversion_map_structure(self):
        """Test audio conversion map structure."""
        assert isinstance(AUDIO_CONVERSION_MAP, dict)
        
        # Test that all keys are in supported audio extensions
        for source_ext in AUDIO_CONVERSION_MAP.keys():
            assert source_ext in SUPPORTED_AUDIO_EXTENSIONS
            
        # Test that all target extensions are lists and contain valid audio extensions
        for source_ext, target_exts in AUDIO_CONVERSION_MAP.items():
            assert isinstance(target_exts, list)
            for target_ext in target_exts:
                assert target_ext in SUPPORTED_AUDIO_EXTENSIONS
                assert target_ext != source_ext  # Source shouldn't convert to itself
    
    def test_video_conversion_map_structure(self):
        """Test video conversion map structure."""
        assert isinstance(VIDEO_CONVERSION_MAP, dict)
        
        # Test that all keys are in supported video extensions
        for source_ext in VIDEO_CONVERSION_MAP.keys():
            assert source_ext in SUPPORTED_VIDEO_EXTENSIONS
            
        # Test that all target extensions are lists and contain valid video extensions
        for source_ext, target_exts in VIDEO_CONVERSION_MAP.items():
            assert isinstance(target_exts, list)
            for target_ext in target_exts:
                assert target_ext in SUPPORTED_VIDEO_EXTENSIONS
                assert target_ext != source_ext  # Source shouldn't convert to itself
    
    def test_image_conversion_map_structure(self):
        """Test image conversion map structure."""
        assert isinstance(IMAGE_CONVERSION_MAP, dict)
        
        # Test that all keys are in supported image extensions
        for source_ext in IMAGE_CONVERSION_MAP.keys():
            assert source_ext in SUPPORTED_IMAGE_EXTENSIONS
            
        # Test that all target extensions are lists and contain valid image extensions
        for source_ext, target_exts in IMAGE_CONVERSION_MAP.items():
            assert isinstance(target_exts, list)
            for target_ext in target_exts:
                assert target_ext in SUPPORTED_IMAGE_EXTENSIONS
                assert target_ext != source_ext  # Source shouldn't convert to itself
    
    def test_text_conversion_map_structure(self):
        """Test text conversion map structure."""
        assert isinstance(TEXT_CONVERSION_MAP, dict)
        
        # Test that all keys are in supported text extensions or special formats
        for source_ext in TEXT_CONVERSION_MAP.keys():
            # Some conversions might include formats like .html, .pdf that aren't in text extensions
            assert isinstance(source_ext, str)
            assert source_ext.startswith('.')
            
        # Test that all target extensions are lists
        for source_ext, target_exts in TEXT_CONVERSION_MAP.items():
            assert isinstance(target_exts, list)
            for target_ext in target_exts:
                assert isinstance(target_ext, str)
                assert target_ext.startswith('.')
    
    def test_conversion_map_consistency(self):
        """Test conversion maps are consistent."""
        # Test that common extensions have conversion mappings
        assert '.mp3' in AUDIO_CONVERSION_MAP
        assert '.wav' in AUDIO_CONVERSION_MAP
        assert '.mp4' in VIDEO_CONVERSION_MAP
        assert '.avi' in VIDEO_CONVERSION_MAP
        assert '.jpg' in IMAGE_CONVERSION_MAP
        assert '.png' in IMAGE_CONVERSION_MAP
        assert '.txt' in TEXT_CONVERSION_MAP
        assert '.json' in TEXT_CONVERSION_MAP