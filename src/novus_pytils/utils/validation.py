"""Validation utilities and error handling.

This module provides comprehensive validation functions and error handling
utilities for file operations and data validation.
"""
import os
import re
import mimetypes
from typing import List, Dict, Tuple
from pathlib import Path
from novus_pytils.core.base import FileHandlerError, UnsupportedFormatError
from novus_pytils.globals import (
    SUPPORTED_TEXT_EXTENSIONS, SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS
)


class ValidationError(FileHandlerError):
    """Exception raised when validation fails."""
    pass


class SecurityError(FileHandlerError):
    """Exception raised when security checks fail."""
    pass


def validate_file_path(file_path: str, must_exist: bool = True, check_permissions: bool = True) -> bool:
    """Validate file path for security and existence.
    
    Args:
        file_path: Path to validate
        must_exist: Whether the file must exist
        check_permissions: Whether to check file permissions
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If validation fails
        SecurityError: If security checks fail
    """
    if not file_path or not isinstance(file_path, str):
        raise ValidationError("File path must be a non-empty string")
    
    path = Path(file_path)
    
    if len(str(path)) > 260:
        raise ValidationError("File path too long (max 260 characters)")
    
    if has_path_traversal(file_path):
        raise SecurityError("Path traversal detected in file path")
    
    if contains_dangerous_chars(file_path):
        raise SecurityError("Dangerous characters detected in file path")
    
    if must_exist and not path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    
    if path.exists() and check_permissions:
        if must_exist and not os.access(file_path, os.R_OK):
            raise ValidationError(f"File is not readable: {file_path}")
        
        if path.parent.exists() and not os.access(path.parent, os.W_OK):
            raise ValidationError(f"Directory is not writable: {path.parent}")
    
    return True


def validate_file_type(file_path: str, expected_types: List[str] = None) -> str:
    """Validate file type based on extension and MIME type.
    
    Args:
        file_path: Path to validate
        expected_types: List of expected file types ('text', 'image', 'audio', 'video')
        
    Returns:
        str: Detected file type
        
    Raises:
        UnsupportedFormatError: If file type is not supported
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    file_type = None
    if ext in SUPPORTED_TEXT_EXTENSIONS:
        file_type = 'text'
    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        file_type = 'image'
    elif ext in SUPPORTED_AUDIO_EXTENSIONS:
        file_type = 'audio'
    elif ext in SUPPORTED_VIDEO_EXTENSIONS:
        file_type = 'video'
    else:
        raise UnsupportedFormatError(f"Unsupported file extension: {ext}")
    
    if expected_types and file_type not in expected_types:
        raise UnsupportedFormatError(f"Expected {expected_types}, got {file_type}")
    
    if os.path.exists(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            mime_file_type = get_type_from_mime(mime_type)
            if mime_file_type != file_type:
                raise UnsupportedFormatError(f"MIME type {mime_type} doesn't match extension {ext}")
    
    return file_type


def validate_image_dimensions(width: int, height: int, max_width: int = 10000, max_height: int = 10000) -> bool:
    """Validate image dimensions.
    
    Args:
        width: Image width
        height: Image height
        max_width: Maximum allowed width
        max_height: Maximum allowed height
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If dimensions are invalid
    """
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValidationError("Width and height must be integers")
    
    if width <= 0 or height <= 0:
        raise ValidationError("Width and height must be positive")
    
    if width > max_width or height > max_height:
        raise ValidationError(f"Dimensions too large (max {max_width}x{max_height})")
    
    return True


def validate_crop_box(box: Tuple[int, int, int, int], image_width: int = None, image_height: int = None) -> bool:
    """Validate crop box coordinates.
    
    Args:
        box: (left, top, right, bottom) coordinates
        image_width: Optional image width for bounds checking
        image_height: Optional image height for bounds checking
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If box is invalid
    """
    if len(box) != 4:
        raise ValidationError("Crop box must have 4 coordinates (left, top, right, bottom)")
    
    left, top, right, bottom = box
    
    if not all(isinstance(coord, int) for coord in box):
        raise ValidationError("Crop coordinates must be integers")
    
    if left >= right or top >= bottom:
        raise ValidationError("Invalid crop box: left >= right or top >= bottom")
    
    if left < 0 or top < 0:
        raise ValidationError("Crop coordinates cannot be negative")
    
    if image_width and image_height:
        if right > image_width or bottom > image_height:
            raise ValidationError(f"Crop box exceeds image bounds ({image_width}x{image_height})")
    
    return True


def validate_audio_parameters(sample_rate: int = None, channels: int = None, bitrate: str = None) -> bool:
    """Validate audio parameters.
    
    Args:
        sample_rate: Sample rate in Hz
        channels: Number of audio channels
        bitrate: Bitrate string (e.g., '192k')
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if sample_rate is not None:
        if not isinstance(sample_rate, int) or sample_rate <= 0:
            raise ValidationError("Sample rate must be a positive integer")
        
        if sample_rate < 8000 or sample_rate > 192000:
            raise ValidationError("Sample rate must be between 8000 and 192000 Hz")
    
    if channels is not None:
        if not isinstance(channels, int) or channels <= 0:
            raise ValidationError("Channels must be a positive integer")
        
        if channels > 8:
            raise ValidationError("Maximum 8 audio channels supported")
    
    if bitrate is not None:
        if not isinstance(bitrate, str):
            raise ValidationError("Bitrate must be a string")
        
        if not re.match(r'^\\d+[kmKM]?$', bitrate):
            raise ValidationError("Invalid bitrate format (e.g., '192k', '320K')")
    
    return True


def validate_video_parameters(fps: float = None, resolution: str = None, bitrate: str = None) -> bool:
    """Validate video parameters.
    
    Args:
        fps: Frames per second
        resolution: Resolution string (e.g., '1920x1080')
        bitrate: Bitrate string (e.g., '2M')
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if fps is not None:
        if not isinstance(fps, (int, float)) or fps <= 0:
            raise ValidationError("FPS must be a positive number")
        
        if fps > 120:
            raise ValidationError("FPS cannot exceed 120")
    
    if resolution is not None:
        if not isinstance(resolution, str):
            raise ValidationError("Resolution must be a string")
        
        if not re.match(r'^\\d+x\\d+$', resolution):
            raise ValidationError("Invalid resolution format (e.g., '1920x1080')")
        
        width, height = map(int, resolution.split('x'))
        validate_image_dimensions(width, height, 7680, 4320)  # 8K max
    
    if bitrate is not None:
        if not isinstance(bitrate, str):
            raise ValidationError("Bitrate must be a string")
        
        if not re.match(r'^\\d+[kmKM]?$', bitrate):
            raise ValidationError("Invalid bitrate format (e.g., '2M', '1000k')")
    
    return True


def validate_time_format(time_str: str) -> bool:
    """Validate time format for video/audio operations.
    
    Args:
        time_str: Time string (e.g., '00:01:30', '90', '1.5')
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If format is invalid
    """
    if not isinstance(time_str, str):
        raise ValidationError("Time must be a string")
    
    if re.match(r'^\\d+$', time_str):
        return True
    
    if re.match(r'^\\d+\\.\\d+$', time_str):
        return True
    
    if re.match(r'^\\d{2}:\\d{2}:\\d{2}$', time_str):
        hours, minutes, seconds = map(int, time_str.split(':'))
        if minutes >= 60 or seconds >= 60:
            raise ValidationError("Invalid time format: minutes/seconds >= 60")
        return True
    
    if re.match(r'^\\d{2}:\\d{2}:\\d{2}\\.\\d+$', time_str):
        time_part, _ = time_str.split('.')
        hours, minutes, seconds = map(int, time_part.split(':'))
        if minutes >= 60 or seconds >= 60:
            raise ValidationError("Invalid time format: minutes/seconds >= 60")
        return True
    
    raise ValidationError("Invalid time format. Use HH:MM:SS, seconds, or decimal seconds")


def validate_file_size(file_path: str, max_size: int = None, min_size: int = 0) -> bool:
    """Validate file size.
    
    Args:
        file_path: Path to file
        max_size: Maximum file size in bytes
        min_size: Minimum file size in bytes
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If size is invalid
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    size = os.path.getsize(file_path)
    
    if size < min_size:
        raise ValidationError(f"File too small: {size} bytes (min {min_size})")
    
    if max_size and size > max_size:
        raise ValidationError(f"File too large: {size} bytes (max {max_size})")
    
    return True


def validate_quality_parameter(quality: int) -> bool:
    """Validate quality parameter (1-100).
    
    Args:
        quality: Quality value
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If quality is invalid
    """
    if not isinstance(quality, int):
        raise ValidationError("Quality must be an integer")
    
    if quality < 1 or quality > 100:
        raise ValidationError("Quality must be between 1 and 100")
    
    return True


def has_path_traversal(path: str) -> bool:
    """Check if path contains path traversal attempts.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if path traversal detected
    """
    dangerous_patterns = ['../', '..\\\\', '../', '..\\', '..']
    path_lower = path.lower()
    
    return any(pattern in path_lower for pattern in dangerous_patterns)


def contains_dangerous_chars(path: str) -> bool:
    """Check if path contains dangerous characters.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if dangerous characters found
    """
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    
    for char in dangerous_chars:
        if char in path:
            return True
    
    if any(ord(char) < 32 for char in path):
        return True
    
    return False


def get_type_from_mime(mime_type: str) -> str:
    """Get file type from MIME type.
    
    Args:
        mime_type: MIME type string
        
    Returns:
        str: File type ('text', 'image', 'audio', 'video')
        
    Raises:
        UnsupportedFormatError: If MIME type is not supported
    """
    if mime_type.startswith('text/'):
        return 'text'
    elif mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type in ['application/json', 'application/xml', 'application/yaml']:
        return 'text'
    else:
        raise UnsupportedFormatError(f"Unsupported MIME type: {mime_type}")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    sanitized = re.sub(r'[\\x00-\\x1f]', '_', sanitized)
    
    sanitized = sanitized.strip('. ')
    
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                     'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                     'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    name_without_ext = os.path.splitext(sanitized)[0].upper()
    if name_without_ext in reserved_names:
        sanitized = f"_{sanitized}"
    
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized or 'unnamed'


def validate_batch_operation(files: List[str], operation: str, **kwargs) -> Dict[str, List[str]]:
    """Validate batch operation parameters.
    
    Args:
        files: List of file paths
        operation: Operation name
        **kwargs: Additional parameters
        
    Returns:
        dict: Validation results with 'valid' and 'invalid' file lists
        
    Raises:
        ValidationError: If operation is invalid
    """
    valid_operations = ['convert', 'copy', 'move', 'delete', 'info']
    
    if operation not in valid_operations:
        raise ValidationError(f"Invalid operation: {operation}. Valid: {valid_operations}")
    
    if not files:
        raise ValidationError("No files provided for batch operation")
    
    if len(files) > 1000:
        raise ValidationError("Too many files for batch operation (max 1000)")
    
    valid_files = []
    invalid_files = []
    
    for file_path in files:
        try:
            validate_file_path(file_path, must_exist=True)
            valid_files.append(file_path)
        except (ValidationError, SecurityError):
            invalid_files.append(file_path)
    
    if operation in ['copy', 'move'] and 'dest_dir' not in kwargs:
        raise ValidationError(f"dest_dir required for {operation} operation")
    
    if operation == 'convert' and 'target_format' not in kwargs:
        raise ValidationError("target_format required for convert operation")
    
    return {
        'valid': valid_files,
        'invalid': invalid_files
    }