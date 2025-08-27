from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import OGG_EXTS

def get_ogg_files(dir):
    """Get a list of OGG audio files in a folder.

    Args:
        dir (str): The path to the folder containing the OGG audio files.

    Returns:
        list: A list of OGG audio file paths.
    """
    return get_files_by_extension(dir, OGG_EXTS)


def is_ogg_file(file):
    """Check if a file is an OGG audio file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is an OGG audio file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in OGG_EXTS)

def filter_ogg_files(files):
    """Filter a list of files to include only OGG audio files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of OGG audio file paths.
    """
    return [file for file in files if is_ogg_file(file)]

def count_ogg_files(dir):
    """Count the number of OGG audio files in a folder.

    Args:
        dir (str): The path to the folder containing the OGG audio files.

    Returns:
        int: The number of OGG audio files in the folder.
    """
    return len(get_ogg_files(dir))

def has_ogg_files(dir):
    """Check if a folder contains any OGG audio files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any OGG audio files, False otherwise.
    """
    return count_ogg_files(dir) > 0


def ogg_to_wav(ogg_file, wav_file):
    """Convert an OGG audio file to WAV format.

    Args:
        ogg_file (str): The path to the input OGG audio file.
        wav_file (str): The path to the output WAV audio file.
    """
    from pydub import AudioSegment

    audio = AudioSegment.from_ogg(ogg_file)
    audio.export(wav_file, format="wav")