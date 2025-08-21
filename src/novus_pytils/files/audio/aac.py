from novus_pytils.files.directories import get_files_by_extension
from novus_pytils.globals import AAC_EXTS

def get_aac_files(dir):
    """Get a list of AAC audio files in a folder.

    Args:
        dir (str): The path to the folder containing the AAC audio files.

    Returns:
        list: A list of AAC audio file paths.
    """
    return get_files_by_extension(dir, AAC_EXTS)