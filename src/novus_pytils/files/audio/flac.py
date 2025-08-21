from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import FLAC_EXTS

def get_flac_files(dir):
    """Get a list of FLAC audio files in a folder.

    Args:
        dir (str): The path to the folder containing the FLAC audio files.

    Returns:
        list: A list of FLAC audio file paths.
    """
    return get_files_by_extension(dir, FLAC_EXTS)