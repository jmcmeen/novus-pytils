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