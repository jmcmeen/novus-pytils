"""Global constants and configuration values.

This module defines constants used throughout the novus_pytils package.
"""

SUPPORTED_AUDIO_EXTENSIONS = ['.wav', '.ogg', '.flac', '.mp3', '.aac', '.wma', '.m4a']
SUPPORTED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']
SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg']
SUPPORTED_TEXT_EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.xml', '.yaml', '.yml', '.log', '.ini', '.cfg']

AUDIO_CONVERSION_MAP = {
    '.wav': ['.mp3', '.ogg', '.flac', '.aac'],
    '.mp3': ['.wav', '.ogg', '.flac', '.aac'],
    '.ogg': ['.wav', '.mp3', '.flac', '.aac'],
    '.flac': ['.wav', '.mp3', '.ogg', '.aac'],
    '.aac': ['.wav', '.mp3', '.ogg', '.flac']
}

VIDEO_CONVERSION_MAP = {
    '.mp4': ['.avi', '.mkv', '.mov', '.webm'],
    '.avi': ['.mp4', '.mkv', '.mov', '.webm'],
    '.mkv': ['.mp4', '.avi', '.mov', '.webm'],
    '.mov': ['.mp4', '.avi', '.mkv', '.webm'],
    '.webm': ['.mp4', '.avi', '.mkv', '.mov']
}

IMAGE_CONVERSION_MAP = {
    '.jpg': ['.png', '.gif', '.bmp', '.tiff', '.webp'],
    '.jpeg': ['.png', '.gif', '.bmp', '.tiff', '.webp'],
    '.png': ['.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'],
    '.gif': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'],
    '.bmp': ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.webp'],
    '.tiff': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
    '.webp': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
}

TEXT_CONVERSION_MAP = {
    '.txt': ['.md', '.csv', '.json', '.xml', '.yaml'],
    '.md': ['.txt', '.html', '.pdf'],
    '.csv': ['.json', '.xml', '.txt'],
    '.json': ['.xml', '.yaml', '.csv', '.txt'],
    '.xml': ['.json', '.yaml', '.csv', '.txt'],
    '.yaml': ['.json', '.xml', '.txt']
}

def get_all_supported_extensions():
    """
    Get all supported file extensions.

    Returns:
        list: A list of all supported file extensions.
    """
    return (SUPPORTED_AUDIO_EXTENSIONS + SUPPORTED_VIDEO_EXTENSIONS + 
            SUPPORTED_IMAGE_EXTENSIONS + SUPPORTED_TEXT_EXTENSIONS)

def is_supported_extension(extension: str) -> bool:
    """
    Check if a file extension is supported.

    Args:
        extension (str): The file extension to check.

    Returns:
        bool: True if the extension is supported, False otherwise.
    """
    return extension.lower() in get_all_supported_extensions()

def get_file_type_by_extension(extension: str) -> str:
    """
    Get the file type based on its extension.

    Args:
        extension (str): The file extension.

    Returns:
        str: The file type ('audio', 'video', 'image', 'text', or 'unknown').
    """
    ext = extension.lower()
    if ext in SUPPORTED_AUDIO_EXTENSIONS:
        return 'audio'
    elif ext in SUPPORTED_VIDEO_EXTENSIONS:
        return 'video'
    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext in SUPPORTED_TEXT_EXTENSIONS:
        return 'text'
    else:
        return 'unknown'

def validate_file_type(file_path: str) -> bool:
    """
    Validate if a file type is supported.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file type is supported, False otherwise.
    """
    import os
    extension = os.path.splitext(file_path)[1].lower()
    return is_supported_extension(extension)