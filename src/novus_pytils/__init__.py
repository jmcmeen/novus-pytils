"""Novus PyTils - A comprehensive file management library.

This package provides comprehensive file management capabilities including:
- CRUD operations for text, image, audio, and video files
- Format conversion between compatible file types
- Batch operations and processing
- Web API for remote file operations
- Command-line interface for all operations
- Object-oriented and functional APIs

Supported file types:
- Text: .txt, .md, .csv, .json, .xml, .yaml, .yml
- Images: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp
- Audio: .wav, .mp3, .ogg, .flac, .aac, .wma, .m4a
- Video: .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm
"""

from novus_pytils.api.functional import (
    read_file, write_file, create_file, update_file, delete_file,
    copy_file, move_file, convert_file, get_file_info, get_supported_conversions,
    batch_convert, batch_operation, resize_image, crop_image, trim_audio, trim_video,
    merge_files, split_file, create_thumbnail, apply_filter, extract_audio_from_video,
    extract_frames_from_video, normalize_audio, change_audio_volume
)

from novus_pytils.api.object_oriented import FileManager, File, FileBatch, MediaCollection

from novus_pytils.models.base import (
    FileHandlerError, UnsupportedFormatError, ConversionError
)

from novus_pytils.validation import ValidationError, SecurityError

__version__ = "1.0.0"
__author__ = "John McMeen"

__all__ = [
    # Functional API
    'read_file', 'write_file', 'create_file', 'update_file', 'delete_file',
    'copy_file', 'move_file', 'convert_file', 'get_file_info', 'get_supported_conversions',
    'batch_convert', 'batch_operation', 'resize_image', 'crop_image', 'trim_audio', 'trim_video',
    'merge_files', 'split_file', 'create_thumbnail', 'apply_filter', 'extract_audio_from_video',
    'extract_frames_from_video', 'normalize_audio', 'change_audio_volume',
    
    # Object-oriented API
    'FileManager', 'File', 'FileBatch', 'MediaCollection',
    
    # Exceptions
    'FileHandlerError', 'UnsupportedFormatError', 'ConversionError',
    'ValidationError', 'SecurityError'
]