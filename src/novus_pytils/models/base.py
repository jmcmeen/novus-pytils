"""Base classes for file operations.

This module provides abstract base classes and interfaces for file handling operations.
"""
import os
import shutil
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pathlib import Path
from .exceptions import FileHandlerError

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