from novus_pytils.files.directories import get_files_by_extension
from novus_pytils.globals import OGG_EXTS

def get_ogg_files(dir):
    """Get a list of OGG audio files in a folder.

    Args:
        dir (str): The path to the folder containing the OGG audio files.

    Returns:
        list: A list of OGG audio file paths.
    """
    return get_files_by_extension(dir, OGG_EXTS)