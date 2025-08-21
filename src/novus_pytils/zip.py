import os
import zipfile

def extract_zip_file(zip_file: str, extract_to: str) -> None:
    """
    Extracts the contents of a ZIP file to a specified directory.

    Args:
        zip_file (str): The path to the ZIP file to be extracted.
        extract_to (str): The directory where the contents will be extracted. 
                          If the directory does not exist, it will be created.
    """

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        os.makedirs(extract_to, exist_ok=True)
        zip_ref.extractall(extract_to)