"""Object-oriented API for file operations.

This module provides an object-oriented interface for file management operations
with support for chaining and context management.
"""
import os
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
from typing import Any, Dict, List, Union
from contextlib import contextmanager
from novus_pytils.exceptions import FileHandlerError, UnsupportedFormatError
from novus_pytils.globals import (
    SUPPORTED_TEXT_EXTENSIONS, SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS
)

class BaseFileHandler(ABC):
    """Abstract base class for file handlers."""
    
    def __init__(self):
        self.supported_extensions = []
        self.conversion_map = {}
    
    @abstractmethod
    def read(self, file_path: str) -> Any:
        """Read and return the contents of a file."""
        pass
    
    @abstractmethod
    def write(self, file_path: str, content: Any, **kwargs) -> bool:
        """Write content to a file."""
        pass
    
    @abstractmethod
    def convert(self, input_path: str, output_path: str, target_format: str, **kwargs) -> bool:
        """Convert a file from one format to another."""
        pass
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if the file can be handled by this handler."""
        if not os.path.exists(file_path):
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions
    
    def get_supported_conversions(self, file_extension: str) -> List[str]:
        """Get list of supported conversion formats for a given file extension."""
        return self.conversion_map.get(file_extension.lower(), [])
    
    def create(self, file_path: str, content: Any = None, **kwargs) -> bool:
        """Create a new file with optional content."""
        try:
            if content is not None:
                return self.write(file_path, content, **kwargs)
            else:
                Path(file_path).touch()
                return True
        except Exception as e:
            raise FileHandlerError(f"Failed to create file {file_path}: {str(e)}")
    
    def update(self, file_path: str, content: Any, **kwargs) -> bool:
        """Update an existing file with new content."""
        if not os.path.exists(file_path):
            raise FileHandlerError(f"File {file_path} does not exist")
        return self.write(file_path, content, **kwargs)
    
    def delete(self, file_path: str) -> bool:
        """Delete a file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            raise FileHandlerError(f"Failed to delete file {file_path}: {str(e)}")
    
    def copy(self, src_path: str, dest_path: str) -> bool:
        """Copy a file from source to destination."""
        try:
            shutil.copy2(src_path, dest_path)
            return True
        except Exception as e:
            raise FileHandlerError(f"Failed to copy file from {src_path} to {dest_path}: {str(e)}")
    
    def move(self, src_path: str, dest_path: str) -> bool:
        """Move a file from source to destination."""
        try:
            shutil.move(src_path, dest_path)
            return True
        except Exception as e:
            raise FileHandlerError(f"Failed to move file from {src_path} to {dest_path}: {str(e)}")
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata."""
        if not os.path.exists(file_path):
            raise FileHandlerError(f"File {file_path} does not exist")
        
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'extension': os.path.splitext(file_path)[1].lower(),
            'basename': os.path.basename(file_path),
            'dirname': os.path.dirname(file_path)
        }




class FileManagerMixin:
    """Mixin class providing common file management operations."""
    
    def batch_convert(self, file_paths: List[str], target_format: str, output_dir: str = None, **kwargs) -> Dict[str, bool]:
        """Convert multiple files to target format."""
        results = {}
        
        for file_path in file_paths:
            try:
                if output_dir:
                    basename = os.path.splitext(os.path.basename(file_path))[0]
                    output_path = os.path.join(output_dir, f"{basename}{target_format}")
                else:
                    output_path = os.path.splitext(file_path)[0] + target_format
                
                results[file_path] = self.convert(file_path, output_path, target_format, **kwargs)
            except Exception:
                results[file_path] = False
        
        return results
    
    def batch_operation(self, file_paths: List[str], operation: str, **kwargs) -> Dict[str, bool]:
        """Perform batch operations on multiple files."""
        results = {}
        
        for file_path in file_paths:
            try:
                if operation == 'delete':
                    results[file_path] = self.delete(file_path)
                elif operation == 'copy' and 'dest_dir' in kwargs:
                    dest_path = os.path.join(kwargs['dest_dir'], os.path.basename(file_path))
                    results[file_path] = self.copy(file_path, dest_path)
                elif operation == 'move' and 'dest_dir' in kwargs:
                    dest_path = os.path.join(kwargs['dest_dir'], os.path.basename(file_path))
                    results[file_path] = self.move(file_path, dest_path)
                else:
                    results[file_path] = False
            except Exception:
                results[file_path] = False
        
        return results

class FileManager:
    """Main file manager class providing unified interface for all file operations."""
    
    def __init__(self):
        from novus_pytils.handlers.text_handler import TextHandler
        from novus_pytils.handlers.image_handler import ImageHandler
        from novus_pytils.handlers.audio_handler import AudioHandler
        from novus_pytils.handlers.video_handler import VideoHandler
        
        self._handlers = {
            'text': TextHandler(),
            'image': ImageHandler(), 
            'audio': AudioHandler(),
            'video': VideoHandler()
        }
        self._cache = {}
    
    def _get_handler(self, file_path: str) -> tuple[BaseFileHandler, str]:
        """Get appropriate handler based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in SUPPORTED_TEXT_EXTENSIONS:
            return self._handlers['text'], 'text'
        elif ext in SUPPORTED_IMAGE_EXTENSIONS:
            return self._handlers['image'], 'image'
        elif ext in SUPPORTED_AUDIO_EXTENSIONS:
            return self._handlers['audio'], 'audio'
        elif ext in SUPPORTED_VIDEO_EXTENSIONS:
            return self._handlers['video'], 'video'
        else:
            raise UnsupportedFormatError(f"Unsupported file format: {ext}")
    
    def get_file(self, file_path: str) -> 'File':
        """Get a File object for the specified path."""
        return File(file_path, self)
    
    def get_batch(self, file_paths: List[str]) -> 'FileBatch':
        """Get a FileBatch object for multiple files."""
        return FileBatch(file_paths, self)


class File:
    """Represents a single file with chainable operations."""
    
    def __init__(self, file_path: str, manager: FileManager):
        self.path = file_path
        self.manager = manager
        self._cached_content = None
        self._modified = False
    
    @property
    def exists(self) -> bool:
        """Check if file exists."""
        return os.path.exists(self.path)
    
    @property
    def extension(self) -> str:
        """Get file extension."""
        return os.path.splitext(self.path)[1].lower()
    
    @property
    def basename(self) -> str:
        """Get file basename."""
        return os.path.basename(self.path)
    
    @property
    def directory(self) -> str:
        """Get file directory."""
        return os.path.dirname(self.path)
    
    @property
    def file_type(self) -> str:
        """Get file type (text, image, audio, video)."""
        try:
            _, file_type = self.manager._get_handler(self.path)
            return file_type
        except UnsupportedFormatError:
            return 'unknown'
    
    def read(self, **kwargs) -> 'File':
        """Read file content and cache it."""
        handler, _ = self.manager._get_handler(self.path)
        self._cached_content = handler.read(self.path, **kwargs)
        return self
    
    def write(self, content: Any = None, **kwargs) -> 'File':
        """Write content to file."""
        content_to_write = content if content is not None else self._cached_content
        if content_to_write is None:
            raise FileHandlerError("No content to write")
        
        handler, _ = self.manager._get_handler(self.path)
        handler.write(self.path, content_to_write, **kwargs)
        self._cached_content = content_to_write
        self._modified = True
        return self
    
    def create(self, content: Any = None, **kwargs) -> 'File':
        """Create new file with optional content."""
        handler, _ = self.manager._get_handler(self.path)
        handler.create(self.path, content, **kwargs)
        self._cached_content = content
        return self
    
    def update(self, content: Any, **kwargs) -> 'File':
        """Update existing file with new content."""
        handler, _ = self.manager._get_handler(self.path)
        handler.update(self.path, content, **kwargs)
        self._cached_content = content
        self._modified = True
        return self
    
    def delete(self) -> 'File':
        """Delete the file."""
        handler, _ = self.manager._get_handler(self.path)
        handler.delete(self.path)
        self._cached_content = None
        return self
    
    def copy_to(self, dest_path: str) -> 'File':
        """Copy file to destination and return new File object."""
        handler, _ = self.manager._get_handler(self.path)
        handler.copy(self.path, dest_path)
        return File(dest_path, self.manager)
    
    def move_to(self, dest_path: str) -> 'File':
        """Move file to destination and update path."""
        handler, _ = self.manager._get_handler(self.path)
        handler.move(self.path, dest_path)
        self.path = dest_path
        return self
    
    def convert_to(self, output_path: str, target_format: str, **kwargs) -> 'File':
        """Convert file to target format and return new File object."""
        handler, _ = self.manager._get_handler(self.path)
        handler.convert(self.path, output_path, target_format, **kwargs)
        return File(output_path, self.manager)
    
    def get_info(self) -> Dict[str, Any]:
        """Get file metadata and information."""
        handler, file_type = self.manager._get_handler(self.path)
        
        if file_type == 'image' and hasattr(handler, 'get_image_info'):
            return handler.get_image_info(self.path)
        elif file_type == 'audio' and hasattr(handler, 'get_audio_info'):
            return handler.get_audio_info(self.path)
        elif file_type == 'video' and hasattr(handler, 'get_video_info'):
            return handler.get_video_info(self.path)
        else:
            return handler.get_metadata(self.path)
    
    def get_supported_conversions(self) -> List[str]:
        """Get supported conversion formats."""
        handler, _ = self.manager._get_handler(self.path)
        return handler.get_supported_conversions(self.extension)
    
    @property
    def content(self) -> Any:
        """Get cached content (read file if not cached)."""
        if self._cached_content is None:
            self.read()
        return self._cached_content
    
    def resize(self, size: tuple, maintain_aspect: bool = True, **kwargs) -> 'File':
        """Resize image (chainable)."""
        if self.file_type != 'image':
            raise UnsupportedFormatError("File is not an image")
        
        handler, _ = self.manager._get_handler(self.path)
        handler.resize(self.path, self.path, size, maintain_aspect, **kwargs)
        self._cached_content = None
        return self
    
    def resize_to(self, output_path: str, size: tuple, maintain_aspect: bool = True, **kwargs) -> 'File':
        """Resize image to new file."""
        if self.file_type != 'image':
            raise UnsupportedFormatError("File is not an image")
        
        handler, _ = self.manager._get_handler(self.path)
        handler.resize(self.path, output_path, size, maintain_aspect, **kwargs)
        return File(output_path, self.manager)
    
    def crop(self, box: tuple, **kwargs) -> 'File':
        """Crop image (chainable)."""
        if self.file_type != 'image':
            raise UnsupportedFormatError("File is not an image")
        
        handler, _ = self.manager._get_handler(self.path)
        handler.crop(self.path, self.path, box, **kwargs)
        self._cached_content = None
        return self
    
    def crop_to(self, output_path: str, box: tuple, **kwargs) -> 'File':
        """Crop image to new file."""
        if self.file_type != 'image':
            raise UnsupportedFormatError("File is not an image")
        
        handler, _ = self.manager._get_handler(self.path)
        handler.crop(self.path, output_path, box, **kwargs)
        return File(output_path, self.manager)
    
    def trim(self, *args, **kwargs) -> 'File':
        """Trim audio/video (chainable)."""
        handler, file_type = self.manager._get_handler(self.path)
        
        if file_type == 'audio':
            handler.trim(self.path, self.path, *args, **kwargs)
        elif file_type == 'video':
            handler.trim(self.path, self.path, *args, **kwargs)
        else:
            raise UnsupportedFormatError(f"Trim not supported for {file_type} files")
        
        self._cached_content = None
        return self
    
    def trim_to(self, output_path: str, *args, **kwargs) -> 'File':
        """Trim audio/video to new file."""
        handler, file_type = self.manager._get_handler(self.path)
        
        if file_type == 'audio':
            handler.trim(self.path, output_path, *args, **kwargs)
        elif file_type == 'video':
            handler.trim(self.path, output_path, *args, **kwargs)
        else:
            raise UnsupportedFormatError(f"Trim not supported for {file_type} files")
        
        return File(output_path, self.manager)
    
    def apply_filter(self, filter_name: str, **kwargs) -> 'File':
        """Apply filter (chainable)."""
        handler, file_type = self.manager._get_handler(self.path)
        
        if file_type in ['image', 'video'] and hasattr(handler, 'apply_filter'):
            handler.apply_filter(self.path, self.path, filter_name, **kwargs)
            self._cached_content = None
            return self
        else:
            raise UnsupportedFormatError(f"Filter not supported for {file_type} files")
    
    def apply_filter_to(self, output_path: str, filter_name: str, **kwargs) -> 'File':
        """Apply filter to new file."""
        handler, file_type = self.manager._get_handler(self.path)
        
        if file_type in ['image', 'video'] and hasattr(handler, 'apply_filter'):
            handler.apply_filter(self.path, output_path, filter_name, **kwargs)
            return File(output_path, self.manager)
        else:
            raise UnsupportedFormatError(f"Filter not supported for {file_type} files")
    
    def create_thumbnail(self, output_path: str, **kwargs) -> 'File':
        """Create thumbnail."""
        handler, file_type = self.manager._get_handler(self.path)
        
        if file_type == 'image' and hasattr(handler, 'create_thumbnail'):
            size = kwargs.get('size', (128, 128))
            handler.create_thumbnail(self.path, output_path, size, **kwargs)
        elif file_type == 'video' and hasattr(handler, 'create_thumbnail'):
            time_position = kwargs.get('time_position', '00:00:01')
            handler.create_thumbnail(self.path, output_path, time_position, **kwargs)
        else:
            raise UnsupportedFormatError(f"Thumbnail not supported for {file_type} files")
        
        return File(output_path, self.manager)
    
    @contextmanager
    def editing(self):
        """Context manager for editing operations."""
        try:
            if not self._cached_content:
                self.read()
            yield self
        finally:
            if self._modified:
                self.write()
    
    def __str__(self) -> str:
        return f"File({self.path})"
    
    def __repr__(self) -> str:
        return f"File(path='{self.path}', type='{self.file_type}', exists={self.exists})"


class FileBatch:
    """Represents multiple files for batch operations."""
    
    def __init__(self, file_paths: List[str], manager: FileManager):
        self.paths = file_paths
        self.manager = manager
        self._files = [File(path, manager) for path in file_paths]
    
    @property
    def files(self) -> List[File]:
        """Get list of File objects."""
        return self._files
    
    def convert_all(self, target_format: str, output_dir: str = None, **kwargs) -> Dict[str, bool]:
        """Convert all files to target format."""
        results = {}
        
        for file_obj in self._files:
            try:
                if output_dir:
                    basename = os.path.splitext(file_obj.basename)[0]
                    output_path = os.path.join(output_dir, f"{basename}{target_format}")
                else:
                    output_path = os.path.splitext(file_obj.path)[0] + target_format
                
                file_obj.convert_to(output_path, target_format, **kwargs)
                results[file_obj.path] = True
            except Exception:
                results[file_obj.path] = False
        
        return results
    
    def copy_all(self, dest_dir: str) -> Dict[str, bool]:
        """Copy all files to destination directory."""
        results = {}
        
        for file_obj in self._files:
            try:
                dest_path = os.path.join(dest_dir, file_obj.basename)
                file_obj.copy_to(dest_path)
                results[file_obj.path] = True
            except Exception:
                results[file_obj.path] = False
        
        return results
    
    def move_all(self, dest_dir: str) -> Dict[str, bool]:
        """Move all files to destination directory."""
        results = {}
        
        for file_obj in self._files:
            try:
                dest_path = os.path.join(dest_dir, file_obj.basename)
                file_obj.move_to(dest_path)
                results[file_obj.path] = True
            except Exception:
                results[file_obj.path] = False
        
        return results
    
    def delete_all(self) -> Dict[str, bool]:
        """Delete all files."""
        results = {}
        
        for file_obj in self._files:
            try:
                file_obj.delete()
                results[file_obj.path] = True
            except Exception:
                results[file_obj.path] = False
        
        return results
    
    def get_all_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information for all files."""
        results = {}
        
        for file_obj in self._files:
            try:
                results[file_obj.path] = file_obj.get_info()
            except Exception:
                results[file_obj.path] = {}
        
        return results
    
    def filter_by_type(self, file_type: str) -> 'FileBatch':
        """Filter files by type."""
        filtered_files = [f for f in self._files if f.file_type == file_type]
        filtered_paths = [f.path for f in filtered_files]
        return FileBatch(filtered_paths, self.manager)
    
    def filter_by_extension(self, extension: str) -> 'FileBatch':
        """Filter files by extension."""
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        filtered_files = [f for f in self._files if f.extension == extension.lower()]
        filtered_paths = [f.path for f in filtered_files]
        return FileBatch(filtered_paths, self.manager)
    
    def __len__(self) -> int:
        return len(self._files)
    
    def __iter__(self):
        return iter(self._files)
    
    def __getitem__(self, index: int) -> File:
        return self._files[index]
    
    def __str__(self) -> str:
        return f"FileBatch({len(self._files)} files)"
    
    def __repr__(self) -> str:
        return f"FileBatch(count={len(self._files)}, types={set(f.file_type for f in self._files)})"


class MediaCollection:
    """Collection class for specific media types."""
    
    def __init__(self, manager: FileManager):
        self.manager = manager
    
    def text(self, file_paths: Union[str, List[str]]) -> Union[File, FileBatch]:
        """Get text file(s)."""
        if isinstance(file_paths, str):
            file_obj = File(file_paths, self.manager)
            if file_obj.file_type != 'text':
                raise UnsupportedFormatError("File is not a text file")
            return file_obj
        else:
            batch = FileBatch(file_paths, self.manager)
            return batch.filter_by_type('text')
    
    def image(self, file_paths: Union[str, List[str]]) -> Union[File, FileBatch]:
        """Get image file(s)."""
        if isinstance(file_paths, str):
            file_obj = File(file_paths, self.manager)
            if file_obj.file_type != 'image':
                raise UnsupportedFormatError("File is not an image file")
            return file_obj
        else:
            batch = FileBatch(file_paths, self.manager)
            return batch.filter_by_type('image')
    
    def audio(self, file_paths: Union[str, List[str]]) -> Union[File, FileBatch]:
        """Get audio file(s)."""
        if isinstance(file_paths, str):
            file_obj = File(file_paths, self.manager)
            if file_obj.file_type != 'audio':
                raise UnsupportedFormatError("File is not an audio file")
            return file_obj
        else:
            batch = FileBatch(file_paths, self.manager)
            return batch.filter_by_type('audio')
    
    def video(self, file_paths: Union[str, List[str]]) -> Union[File, FileBatch]:
        """Get video file(s)."""
        if isinstance(file_paths, str):
            file_obj = File(file_paths, self.manager)
            if file_obj.file_type != 'video':
                raise UnsupportedFormatError("File is not a video file")
            return file_obj
        else:
            batch = FileBatch(file_paths, self.manager)
            return batch.filter_by_type('video')