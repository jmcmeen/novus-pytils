from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import MP3_EXTS

def get_mp3_files(dir):
    """Get a list of MP3 audio files in a folder.

    Args:
        dir (str): The path to the folder containing the MP3 audio files.

    Returns:
        list: A list of MP3 audio file paths.
    """
    return get_files_by_extension(dir, MP3_EXTS)