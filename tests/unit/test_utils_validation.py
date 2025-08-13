"""Unit tests for utils.validation module."""
import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile

from novus_pytils.utils.validation import (
    validate_file_path, validate_file_extension, validate_file_size,
    validate_image_dimensions, validate_audio_parameters, validate_video_parameters,
    validate_quality_parameter, validate_color_format, validate_url,
    validate_email, validate_json_structure, sanitize_filename,
    is_safe_path, check_disk_space, ValidationResult
)


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_validation_result_valid(self):
        """Test ValidationResult for valid case."""
        result = ValidationResult(True, "Validation passed")
        
        assert result.is_valid is True
        assert result.message == "Validation passed"
        assert result.errors == []
    
    def test_validation_result_invalid(self):
        """Test ValidationResult for invalid case."""
        errors = ["Error 1", "Error 2"]
        result = ValidationResult(False, "Validation failed", errors)
        
        assert result.is_valid is False
        assert result.message == "Validation failed"
        assert result.errors == errors
    
    def test_validation_result_string_representation(self):
        """Test string representation of ValidationResult."""
        result = ValidationResult(True, "Success")
        assert str(result) == "ValidationResult(valid=True, message='Success')"
        
        result = ValidationResult(False, "Failed", ["Error"])
        assert str(result) == "ValidationResult(valid=False, message='Failed')"


class TestFilePathValidation:
    """Test file path validation functions."""
    
    @patch('os.path.exists')
    def test_validate_file_path_exists(self, mock_exists):
        """Test file path validation when file exists."""
        mock_exists.return_value = True
        
        result = validate_file_path("/path/to/file.txt")
        
        assert result.is_valid is True
        assert "exists" in result.message.lower()
        mock_exists.assert_called_once_with("/path/to/file.txt")
    
    @patch('os.path.exists')
    def test_validate_file_path_not_exists(self, mock_exists):
        """Test file path validation when file doesn't exist."""
        mock_exists.return_value = False
        
        result = validate_file_path("/path/to/nonexistent.txt")
        
        assert result.is_valid is False
        assert "not exist" in result.message.lower()
    
    @patch('os.path.exists')
    def test_validate_file_path_allow_nonexistent(self, mock_exists):
        """Test file path validation allowing nonexistent files."""
        mock_exists.return_value = False
        
        result = validate_file_path("/path/to/new_file.txt", must_exist=False)
        
        assert result.is_valid is True
    
    def test_validate_file_path_empty(self):
        """Test file path validation with empty path."""
        result = validate_file_path("")
        
        assert result.is_valid is False
        assert "empty" in result.message.lower()
    
    def test_validate_file_path_none(self):
        """Test file path validation with None."""
        result = validate_file_path(None)
        
        assert result.is_valid is False


class TestFileExtensionValidation:
    """Test file extension validation."""
    
    def test_validate_file_extension_valid(self):
        """Test valid file extension."""
        valid_extensions = [".txt", ".pdf", ".docx"]
        
        result = validate_file_extension("document.txt", valid_extensions)
        
        assert result.is_valid is True
        assert "valid" in result.message.lower()
    
    def test_validate_file_extension_invalid(self):
        """Test invalid file extension."""
        valid_extensions = [".txt", ".pdf", ".docx"]
        
        result = validate_file_extension("document.xyz", valid_extensions)
        
        assert result.is_valid is False
        assert "not supported" in result.message.lower()
    
    def test_validate_file_extension_case_insensitive(self):
        """Test file extension validation is case insensitive."""
        valid_extensions = [".txt", ".pdf"]
        
        result = validate_file_extension("document.TXT", valid_extensions)
        
        assert result.is_valid is True
    
    def test_validate_file_extension_no_extension(self):
        """Test file with no extension."""
        valid_extensions = [".txt", ".pdf"]
        
        result = validate_file_extension("document", valid_extensions)
        
        assert result.is_valid is False


class TestFileSizeValidation:
    """Test file size validation."""
    
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_validate_file_size_within_limit(self, mock_exists, mock_getsize):
        """Test file size validation within limit."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024  # 1KB
        
        result = validate_file_size("test.txt", max_size_mb=1)
        
        assert result.is_valid is True
        mock_getsize.assert_called_once_with("test.txt")
    
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_validate_file_size_exceeds_limit(self, mock_exists, mock_getsize):
        """Test file size validation exceeding limit."""
        mock_exists.return_value = True
        mock_getsize.return_value = 2 * 1024 * 1024  # 2MB
        
        result = validate_file_size("large_file.txt", max_size_mb=1)
        
        assert result.is_valid is False
        assert "exceeds" in result.message.lower()
    
    @patch('os.path.exists')
    def test_validate_file_size_file_not_exists(self, mock_exists):
        """Test file size validation for nonexistent file."""
        mock_exists.return_value = False
        
        result = validate_file_size("nonexistent.txt", max_size_mb=1)
        
        assert result.is_valid is False
        assert "not exist" in result.message.lower()
    
    def test_validate_file_size_invalid_max_size(self):
        """Test file size validation with invalid max size."""
        result = validate_file_size("test.txt", max_size_mb=-1)
        
        assert result.is_valid is False
        assert "invalid" in result.message.lower()


class TestImageDimensionsValidation:
    """Test image dimensions validation."""
    
    def test_validate_image_dimensions_valid(self):
        """Test valid image dimensions."""
        result = validate_image_dimensions(1920, 1080, max_width=2000, max_height=1500)
        
        assert result.is_valid is True
    
    def test_validate_image_dimensions_width_exceeds(self):
        """Test image width exceeding limit."""
        result = validate_image_dimensions(2500, 1080, max_width=2000, max_height=1500)
        
        assert result.is_valid is False
        assert "width" in result.message.lower()
    
    def test_validate_image_dimensions_height_exceeds(self):
        """Test image height exceeding limit."""
        result = validate_image_dimensions(1920, 2000, max_width=2000, max_height=1500)
        
        assert result.is_valid is False
        assert "height" in result.message.lower()
    
    def test_validate_image_dimensions_negative(self):
        """Test negative image dimensions."""
        result = validate_image_dimensions(-100, 200)
        
        assert result.is_valid is False
        assert "positive" in result.message.lower()
    
    def test_validate_image_dimensions_zero(self):
        """Test zero image dimensions."""
        result = validate_image_dimensions(0, 100)
        
        assert result.is_valid is False
        assert "positive" in result.message.lower()


class TestAudioParametersValidation:
    """Test audio parameters validation."""
    
    def test_validate_audio_parameters_valid(self):
        """Test valid audio parameters."""
        result = validate_audio_parameters(
            sample_rate=44100,
            channels=2,
            bitrate="192k",
            duration=300
        )
        
        assert result.is_valid is True
    
    def test_validate_audio_parameters_invalid_sample_rate(self):
        """Test invalid sample rate."""
        result = validate_audio_parameters(sample_rate=1000)
        
        assert result.is_valid is False
        assert "sample rate" in result.message.lower()
    
    def test_validate_audio_parameters_invalid_channels(self):
        """Test invalid channel count."""
        result = validate_audio_parameters(channels=0)
        
        assert result.is_valid is False
        assert "channels" in result.message.lower()
    
    def test_validate_audio_parameters_invalid_bitrate(self):
        """Test invalid bitrate format."""
        result = validate_audio_parameters(bitrate="invalid")
        
        assert result.is_valid is False
        assert "bitrate" in result.message.lower()
    
    def test_validate_audio_parameters_negative_duration(self):
        """Test negative duration."""
        result = validate_audio_parameters(duration=-10)
        
        assert result.is_valid is False
        assert "duration" in result.message.lower()


class TestVideoParametersValidation:
    """Test video parameters validation."""
    
    def test_validate_video_parameters_valid(self):
        """Test valid video parameters."""
        result = validate_video_parameters(
            fps=30,
            resolution="1920x1080",
            bitrate="5000k",
            duration=3600
        )
        
        assert result.is_valid is True
    
    def test_validate_video_parameters_invalid_fps(self):
        """Test invalid FPS."""
        result = validate_video_parameters(fps=0)
        
        assert result.is_valid is False
        assert "fps" in result.message.lower()
    
    def test_validate_video_parameters_invalid_resolution(self):
        """Test invalid resolution format."""
        result = validate_video_parameters(resolution="invalid")
        
        assert result.is_valid is False
        assert "resolution" in result.message.lower()
    
    def test_validate_video_parameters_invalid_bitrate(self):
        """Test invalid bitrate."""
        result = validate_video_parameters(bitrate="invalid")
        
        assert result.is_valid is False
        assert "bitrate" in result.message.lower()


class TestQualityParameterValidation:
    """Test quality parameter validation."""
    
    def test_validate_quality_parameter_valid(self):
        """Test valid quality parameter."""
        result = validate_quality_parameter(85)
        
        assert result.is_valid is True
    
    def test_validate_quality_parameter_min_boundary(self):
        """Test quality parameter at minimum boundary."""
        result = validate_quality_parameter(1)
        
        assert result.is_valid is True
    
    def test_validate_quality_parameter_max_boundary(self):
        """Test quality parameter at maximum boundary."""
        result = validate_quality_parameter(100)
        
        assert result.is_valid is True
    
    def test_validate_quality_parameter_below_min(self):
        """Test quality parameter below minimum."""
        result = validate_quality_parameter(0)
        
        assert result.is_valid is False
        assert "between 1 and 100" in result.message
    
    def test_validate_quality_parameter_above_max(self):
        """Test quality parameter above maximum."""
        result = validate_quality_parameter(101)
        
        assert result.is_valid is False
        assert "between 1 and 100" in result.message


class TestColorFormatValidation:
    """Test color format validation."""
    
    def test_validate_color_format_rgb(self):
        """Test RGB color format validation."""
        result = validate_color_format("rgb(255, 128, 0)")
        
        assert result.is_valid is True
    
    def test_validate_color_format_hex(self):
        """Test hex color format validation."""
        result = validate_color_format("#FF8000")
        
        assert result.is_valid is True
    
    def test_validate_color_format_hex_short(self):
        """Test short hex color format validation."""
        result = validate_color_format("#F80")
        
        assert result.is_valid is True
    
    def test_validate_color_format_named(self):
        """Test named color validation."""
        result = validate_color_format("red")
        
        assert result.is_valid is True
    
    def test_validate_color_format_invalid(self):
        """Test invalid color format."""
        result = validate_color_format("invalid_color")
        
        assert result.is_valid is False


class TestUrlValidation:
    """Test URL validation."""
    
    def test_validate_url_http(self):
        """Test HTTP URL validation."""
        result = validate_url("http://example.com")
        
        assert result.is_valid is True
    
    def test_validate_url_https(self):
        """Test HTTPS URL validation."""
        result = validate_url("https://www.example.com/path?param=value")
        
        assert result.is_valid is True
    
    def test_validate_url_ftp(self):
        """Test FTP URL validation."""
        result = validate_url("ftp://ftp.example.com/file.txt")
        
        assert result.is_valid is True
    
    def test_validate_url_invalid(self):
        """Test invalid URL."""
        result = validate_url("not_a_url")
        
        assert result.is_valid is False
    
    def test_validate_url_empty(self):
        """Test empty URL."""
        result = validate_url("")
        
        assert result.is_valid is False


class TestEmailValidation:
    """Test email validation."""
    
    def test_validate_email_valid(self):
        """Test valid email address."""
        result = validate_email("user@example.com")
        
        assert result.is_valid is True
    
    def test_validate_email_with_subdomain(self):
        """Test email with subdomain."""
        result = validate_email("user@mail.example.com")
        
        assert result.is_valid is True
    
    def test_validate_email_with_plus(self):
        """Test email with plus sign."""
        result = validate_email("user+tag@example.com")
        
        assert result.is_valid is True
    
    def test_validate_email_invalid_no_at(self):
        """Test invalid email without @ symbol."""
        result = validate_email("userexample.com")
        
        assert result.is_valid is False
    
    def test_validate_email_invalid_no_domain(self):
        """Test invalid email without domain."""
        result = validate_email("user@")
        
        assert result.is_valid is False


class TestJsonStructureValidation:
    """Test JSON structure validation."""
    
    def test_validate_json_structure_valid(self):
        """Test valid JSON structure."""
        json_data = {"name": "John", "age": 30, "city": "New York"}
        required_fields = ["name", "age"]
        
        result = validate_json_structure(json_data, required_fields)
        
        assert result.is_valid is True
    
    def test_validate_json_structure_missing_field(self):
        """Test JSON structure with missing required field."""
        json_data = {"name": "John"}
        required_fields = ["name", "age"]
        
        result = validate_json_structure(json_data, required_fields)
        
        assert result.is_valid is False
        assert "age" in str(result.errors)
    
    def test_validate_json_structure_with_types(self):
        """Test JSON structure with type validation."""
        json_data = {"name": "John", "age": 30}
        required_fields = ["name", "age"]
        field_types = {"name": str, "age": int}
        
        result = validate_json_structure(json_data, required_fields, field_types)
        
        assert result.is_valid is True
    
    def test_validate_json_structure_wrong_type(self):
        """Test JSON structure with wrong field type."""
        json_data = {"name": "John", "age": "thirty"}
        required_fields = ["name", "age"]
        field_types = {"name": str, "age": int}
        
        result = validate_json_structure(json_data, required_fields, field_types)
        
        assert result.is_valid is False


class TestFilenameValidation:
    """Test filename validation and sanitization."""
    
    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        result = sanitize_filename("normal_filename.txt")
        
        assert result == "normal_filename.txt"
    
    def test_sanitize_filename_invalid_chars(self):
        """Test filename sanitization with invalid characters."""
        result = sanitize_filename("file<name>with|invalid:chars?.txt")
        
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result
        assert ":" not in result
        assert "?" not in result
    
    def test_sanitize_filename_reserved_names(self):
        """Test filename sanitization with reserved names."""
        result = sanitize_filename("CON.txt")
        
        assert result != "CON.txt"
    
    def test_sanitize_filename_too_long(self):
        """Test filename sanitization with too long name."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        
        assert len(result) <= 255
        assert result.endswith(".txt")


class TestPathSafety:
    """Test path safety validation."""
    
    def test_is_safe_path_safe(self):
        """Test safe path validation."""
        result = is_safe_path("/safe/path/to/file.txt", "/safe")
        
        assert result is True
    
    def test_is_safe_path_traversal_attack(self):
        """Test path traversal attack detection."""
        result = is_safe_path("/safe/../../../etc/passwd", "/safe")
        
        assert result is False
    
    def test_is_safe_path_relative_traversal(self):
        """Test relative path traversal detection."""
        result = is_safe_path("../../../etc/passwd", "/safe")
        
        assert result is False
    
    def test_is_safe_path_same_directory(self):
        """Test same directory access."""
        result = is_safe_path("/safe/file.txt", "/safe")
        
        assert result is True


class TestDiskSpaceValidation:
    """Test disk space validation."""
    
    @patch('shutil.disk_usage')
    def test_check_disk_space_sufficient(self, mock_disk_usage):
        """Test disk space check with sufficient space."""
        # Mock disk usage: (total, used, free) in bytes
        mock_disk_usage.return_value = (1000000, 500000, 500000)
        
        result = check_disk_space("/path", required_mb=100)
        
        assert result.is_valid is True
    
    @patch('shutil.disk_usage')
    def test_check_disk_space_insufficient(self, mock_disk_usage):
        """Test disk space check with insufficient space."""
        # Mock disk usage: (total, used, free) in bytes
        mock_disk_usage.return_value = (1000000, 950000, 50000)
        
        result = check_disk_space("/path", required_mb=100)
        
        assert result.is_valid is False
        assert "insufficient" in result.message.lower()
    
    @patch('shutil.disk_usage')
    def test_check_disk_space_error(self, mock_disk_usage):
        """Test disk space check with error."""
        mock_disk_usage.side_effect = OSError("Disk not accessible")
        
        result = check_disk_space("/invalid/path", required_mb=100)
        
        assert result.is_valid is False
        assert "error" in result.message.lower()