from novus_pytils.files.directories import get_files_by_extension
from novus_pytils.globals import WMA_EXTS

def get_wma_files(dir):
    """Get a list of WMA audio files in a folder.

    Args:
        dir (str): The path to the folder containing the WMA audio files.

    Returns:
        list: A list of WMA audio file paths.
    """
    return get_files_by_extension(dir, WMA_EXTS)