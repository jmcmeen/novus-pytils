from novus_pytils.files.directories import get_files_by_extension
from novus_pytils.globals import M4A_EXTS

def get_m4a_files(dir):
    """Get a list of M4A audio files in a folder.

    Args:
        dir (str): The path to the folder containing the M4A audio files.

    Returns:
        list: A list of M4A audio file paths.
    """
    return get_files_by_extension(dir, M4A_EXTS)