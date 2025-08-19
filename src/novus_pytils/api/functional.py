"""Functional API for file operations.

This module provides a functional interface for file management operations
across different media types including text, images, audio, and video.
"""
import os
from typing import Any, Dict, List
from novus_pytils.handlers.text_handler import TextHandler
from novus_pytils.handlers.image_handler import ImageHandler
from novus_pytils.handlers.audio_handler import AudioHandler
from novus_pytils.handlers.video_handler import VideoHandler
from novus_pytils.core.base import UnsupportedFormatError
from novus_pytils.globals import (
    SUPPORTED_TEXT_EXTENSIONS, SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS
)


_handlers = {
    'text': TextHandler(),
    'image': ImageHandler(), 
    'audio': AudioHandler(),
    'video': VideoHandler()
}


def _get_handler(file_path: str):
    """Get appropriate handler based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in SUPPORTED_TEXT_EXTENSIONS:
        return _handlers['text'], 'text'
    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        return _handlers['image'], 'image'
    elif ext in SUPPORTED_AUDIO_EXTENSIONS:
        return _handlers['audio'], 'audio'
    elif ext in SUPPORTED_VIDEO_EXTENSIONS:
        return _handlers['video'], 'video'
    else:
        raise UnsupportedFormatError(f"Unsupported file format: {ext}")


def read_file(file_path: str, **kwargs) -> Any:
    """Read a file and return its contents."""
    handler, _ = _get_handler(file_path)
    return handler.read(file_path, **kwargs)


def write_file(file_path: str, content: Any, **kwargs) -> bool:
    """Write content to a file."""
    handler, _ = _get_handler(file_path)
    return handler.write(file_path, content, **kwargs)


def create_file(file_path: str, content: Any = None, **kwargs) -> bool:
    """Create a new file with optional content."""
    handler, _ = _get_handler(file_path)
    return handler.create(file_path, content, **kwargs)


def update_file(file_path: str, content: Any, **kwargs) -> bool:
    """Update an existing file with new content."""
    handler, _ = _get_handler(file_path)
    return handler.update(file_path, content, **kwargs)


def delete_file(file_path: str) -> bool:
    """Delete a file."""
    handler, _ = _get_handler(file_path)
    return handler.delete(file_path)


def copy_file(src_path: str, dest_path: str) -> bool:
    """Copy a file from source to destination."""
    handler, _ = _get_handler(src_path)
    return handler.copy(src_path, dest_path)


def move_file(src_path: str, dest_path: str) -> bool:
    """Move a file from source to destination."""
    handler, _ = _get_handler(src_path)
    return handler.move(src_path, dest_path)


def convert_file(input_path: str, output_path: str, target_format: str, **kwargs) -> bool:
    """Convert a file from one format to another."""
    handler, _ = _get_handler(input_path)
    return handler.convert(input_path, output_path, target_format, **kwargs)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get file metadata and information."""
    handler, file_type = _get_handler(file_path)
    
    if file_type == 'image' and hasattr(handler, 'get_image_info'):
        return handler.get_image_info(file_path)
    elif file_type == 'audio' and hasattr(handler, 'get_audio_info'):
        return handler.get_audio_info(file_path)
    elif file_type == 'video' and hasattr(handler, 'get_video_info'):
        return handler.get_video_info(file_path)
    else:
        return handler.get_metadata(file_path)


def get_supported_conversions(file_path: str) -> List[str]:
    """Get supported conversion formats for a file."""
    handler, _ = _get_handler(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    return handler.get_supported_conversions(ext)


def batch_convert(file_paths: List[str], target_format: str, output_dir: str = None, **kwargs) -> Dict[str, bool]:
    """Convert multiple files to target format."""
    results = {}
    
    for file_path in file_paths:
        try:
            handler, _ = _get_handler(file_path)
            if hasattr(handler, 'batch_convert'):
                batch_result = handler.batch_convert([file_path], target_format, output_dir, **kwargs)
                results.update(batch_result)
            else:
                if output_dir:
                    basename = os.path.splitext(os.path.basename(file_path))[0]
                    output_path = os.path.join(output_dir, f"{basename}{target_format}")
                else:
                    output_path = os.path.splitext(file_path)[0] + target_format
                
                results[file_path] = handler.convert(file_path, output_path, target_format, **kwargs)
        except Exception:
            results[file_path] = False
    
    return results


def batch_operation(file_paths: List[str], operation: str, **kwargs) -> Dict[str, bool]:
    """Perform batch operations on multiple files."""
    results = {}
    
    for file_path in file_paths:
        try:
            handler, _ = _get_handler(file_path)
            
            if operation == 'delete':
                results[file_path] = handler.delete(file_path)
            elif operation == 'copy' and 'dest_dir' in kwargs:
                dest_path = os.path.join(kwargs['dest_dir'], os.path.basename(file_path))
                results[file_path] = handler.copy(file_path, dest_path)
            elif operation == 'move' and 'dest_dir' in kwargs:
                dest_path = os.path.join(kwargs['dest_dir'], os.path.basename(file_path))
                results[file_path] = handler.move(file_path, dest_path)
            elif operation == 'info':
                results[file_path] = get_file_info(file_path)
            else:
                results[file_path] = False
        except Exception:
            results[file_path] = False
    
    return results


def resize_image(input_path: str, output_path: str, size: tuple, maintain_aspect: bool = True, **kwargs) -> bool:
    """Resize an image file."""
    handler, file_type = _get_handler(input_path)
    if file_type != 'image':
        raise UnsupportedFormatError("File is not an image")
    return handler.resize(input_path, output_path, size, maintain_aspect, **kwargs)


def crop_image(input_path: str, output_path: str, box: tuple, **kwargs) -> bool:
    """Crop an image file."""
    handler, file_type = _get_handler(input_path)
    if file_type != 'image':
        raise UnsupportedFormatError("File is not an image")
    return handler.crop(input_path, output_path, box, **kwargs)


def trim_audio(input_path: str, output_path: str, start_ms: int, end_ms: int, **kwargs) -> bool:
    """Trim an audio file."""
    handler, file_type = _get_handler(input_path)
    if file_type != 'audio':
        raise UnsupportedFormatError("File is not audio")
    return handler.trim(input_path, output_path, start_ms, end_ms, **kwargs)


def trim_video(input_path: str, output_path: str, start_time: str, duration: str = None, end_time: str = None, **kwargs) -> bool:
    """Trim a video file."""
    handler, file_type = _get_handler(input_path)
    if file_type != 'video':
        raise UnsupportedFormatError("File is not a video")
    return handler.trim(input_path, output_path, start_time, duration, end_time, **kwargs)


def merge_files(file_paths: List[str], output_path: str, **kwargs) -> bool:
    """Merge multiple files of the same type."""
    if not file_paths:
        return False
    
    handler, file_type = _get_handler(file_paths[0])
    
    if file_type == 'text' and hasattr(handler, 'merge_files'):
        separator = kwargs.get('separator', '\n')
        return handler.merge_files(file_paths, output_path, separator)
    elif file_type == 'audio' and hasattr(handler, 'concatenate'):
        return handler.concatenate(file_paths, output_path, **kwargs)
    elif file_type == 'video' and hasattr(handler, 'concatenate'):
        return handler.concatenate(file_paths, output_path, **kwargs)
    elif file_type == 'image' and hasattr(handler, 'merge_images'):
        orientation = kwargs.get('orientation', 'horizontal')
        return handler.merge_images(file_paths, output_path, orientation, **kwargs)
    else:
        raise UnsupportedFormatError(f"Merge not supported for {file_type} files")


def split_file(file_path: str, output_dir: str, **kwargs) -> List[str]:
    """Split a file into multiple parts."""
    handler, file_type = _get_handler(file_path)
    
    if file_type == 'text' and hasattr(handler, 'split_file'):
        lines_per_file = kwargs.get('lines_per_file', 1000)
        return handler.split_file(file_path, output_dir, lines_per_file)
    elif file_type == 'audio' and hasattr(handler, 'split_on_silence'):
        min_silence_len = kwargs.get('min_silence_len', 1000)
        silence_thresh = kwargs.get('silence_thresh', -40)
        return handler.split_on_silence(file_path, output_dir, min_silence_len, silence_thresh, **kwargs)
    else:
        raise UnsupportedFormatError(f"Split not supported for {file_type} files")


def create_thumbnail(input_path: str, output_path: str, **kwargs) -> bool:
    """Create thumbnail from image or video."""
    handler, file_type = _get_handler(input_path)
    
    if file_type == 'image' and hasattr(handler, 'create_thumbnail'):
        size = kwargs.get('size', (128, 128))
        return handler.create_thumbnail(input_path, output_path, size, **kwargs)
    elif file_type == 'video' and hasattr(handler, 'create_thumbnail'):
        time_position = kwargs.get('time_position', '00:00:01')
        return handler.create_thumbnail(input_path, output_path, time_position, **kwargs)
    else:
        raise UnsupportedFormatError(f"Thumbnail creation not supported for {file_type} files")


def apply_filter(input_path: str, output_path: str, filter_name: str, **kwargs) -> bool:
    """Apply filter to image or video."""
    handler, file_type = _get_handler(input_path)
    
    if file_type in ['image', 'video'] and hasattr(handler, 'apply_filter'):
        return handler.apply_filter(input_path, output_path, filter_name, **kwargs)
    else:
        raise UnsupportedFormatError(f"Filter application not supported for {file_type} files")


def extract_audio_from_video(input_path: str, output_path: str, **kwargs) -> bool:
    """Extract audio from video file."""
    handler, file_type = _get_handler(input_path)
    if file_type != 'video':
        raise UnsupportedFormatError("File is not a video")
    return handler.extract_audio(input_path, output_path, **kwargs)


def extract_frames_from_video(input_path: str, output_dir: str, fps: float = 1.0, **kwargs) -> List[str]:
    """Extract frames from video as images."""
    handler, file_type = _get_handler(input_path)
    if file_type != 'video':
        raise UnsupportedFormatError("File is not a video")
    return handler.extract_frames(input_path, output_dir, fps, **kwargs)


def normalize_audio(input_path: str, output_path: str, target_dBFS: float = -20.0, **kwargs) -> bool:
    """Normalize audio file."""
    handler, file_type = _get_handler(input_path)
    if file_type != 'audio':
        raise UnsupportedFormatError("File is not audio")
    return handler.normalize(input_path, output_path, target_dBFS, **kwargs)


def change_audio_volume(input_path: str, output_path: str, volume_change_db: float, **kwargs) -> bool:
    """Change volume of audio file."""
    handler, file_type = _get_handler(input_path)
    if file_type != 'audio':
        raise UnsupportedFormatError("File is not audio")
    return handler.change_volume(input_path, output_path, volume_change_db, **kwargs)