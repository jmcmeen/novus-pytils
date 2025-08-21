def read_file_bytes(file_path) -> bytes:
    """Read the contents of a file and return it as bytes.

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        bytes: The contents of the file as bytes.
    """
    with open(file_path, 'rb') as file:
        return file.read()
    
def read_file_text(file_path, encoding='utf-8') -> str:
    """Read the contents of a text file and return it as a string.

    Args:
        file_path (str): The path to the text file to be read.
        encoding (str, optional): The encoding of the text file. Defaults to 'utf-8'.

    Returns:
        str: The contents of the text file as a string.
    """
    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()