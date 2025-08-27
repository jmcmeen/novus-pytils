from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import WMA_EXTS

def get_wma_files(dir):
    """Get a list of WMA audio files in a folder.

    Args:
        dir (str): The path to the folder containing the WMA audio files.

    Returns:
        list: A list of WMA audio file paths.
    """
    return get_files_by_extension(dir, WMA_EXTS)

def is_wma_file(file):
    """Check if a file is a WMA audio file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is a WMA audio file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in WMA_EXTS)

def filter_wma_files(files):
    """Filter a list of files to include only WMA audio files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of WMA audio file paths.
    """
    return [file for file in files if is_wma_file(file)]

def count_wma_files(dir):
    """Count the number of WMA audio files in a folder.

    Args:
        dir (str): The path to the folder containing the WMA audio files.

    Returns:
        int: The number of WMA audio files in the folder.
    """
    return len(get_wma_files(dir))

def has_wma_files(dir):
    """Check if a folder contains any WMA audio files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any WMA audio files, False otherwise.
    """
    return count_wma_files(dir) > 0

def wma_to_wav(wma_file, wav_file):
    """Convert a WMA audio file to WAV format.

    Args:
        wma_file (str): The path to the input WMA audio file.
        wav_file (str): The path to the output WAV audio file.

    Returns:
        None
    """
    from pydub import AudioSegment

    audio = AudioSegment.from_file(wma_file, format="wma")
    audio.export(wav_file, format="wav")
    
