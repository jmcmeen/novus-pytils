"""Console utility functions for terminal output.

This module provides functions for creating progress bars and other console output utilities.
"""
import os
from enum import Enum
from typing import List

class ColorCode(Enum):
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(text: str, color: ColorCode) -> None:
    """
    Print text in the specified color.

    Args:
        text (str): The text to print.
        color (ColorCode): The color to use.
    """
    print(f"{color.value}{text}{ColorCode.RESET.value}")

def print_success(text: str) -> None:
    """
    Print success message in green.

    Args:
        text (str): The success message to print.
    """
    print_color(f"✓ {text}", ColorCode.GREEN)

def print_error(text: str) -> None:
    """
    Print error message in red.

    Args:
        text (str): The error message to print.
    """
    print_color(f"✗ {text}", ColorCode.RED)

def print_warning(text: str) -> None:
    """
    Print warning message in yellow.

    Args:
        text (str): The warning message to print.
    """
    print_color(f"⚠ {text}", ColorCode.YELLOW)

def print_info(text: str) -> None:
    """
    Print info message in blue.

    Args:
        text (str): The info message to print.
    """
    print_color(f"ℹ {text}", ColorCode.BLUE)

def print_table(headers: List[str], rows: List[List[str]], separator: str = '|') -> None:
    """
    Print a formatted table.

    Args:
        headers (List[str]): The table headers.
        rows (List[List[str]]): The table rows.
        separator (str): The column separator.
    """
    if not headers or not rows:
        return

    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print headers
    header_row = separator.join(f" {header.ljust(col_widths[i])} " for i, header in enumerate(headers))
    print(header_row)
    print('-' * len(header_row))

    # Print rows
    for row in rows:
        row_str = separator.join(f" {str(cell).ljust(col_widths[i])} " for i, cell in enumerate(row))
        print(row_str)

def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', 
                      decimals: int = 1, length: int = 100, fill: str = '█', print_end: str = "\r") -> None:
    """
    Create terminal progress bar.

    Args:
        iteration (int): Current iteration.
        total (int): Total iterations.
        prefix (str): Prefix string.
        suffix (str): Suffix string.
        decimals (int): Number of decimals in percent complete.
        length (int): Character length of bar.
        fill (str): Bar fill character.
        print_end (str): End character.
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    if iteration == total:
        print()

def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.

    Args:
        message (str): The confirmation message.
        default (bool): Default response if user just presses Enter.

    Returns:
        bool: True if user confirms, False otherwise.
    """
    prompt = f"{message} [{'Y/n' if default else 'y/N'}]: "
    response = input(prompt).strip().lower()
    
    if not response:
        return default
    return response in ['y', 'yes', 'true', '1']

def get_user_input(prompt: str, default: str = None, required: bool = False) -> str:
    """
    Get user input with optional default value.

    Args:
        prompt (str): The input prompt.
        default (str): Default value if user just presses Enter.
        required (bool): Whether input is required.

    Returns:
        str: The user input.
    """
    while True:
        display_prompt = f"{prompt}"
        if default:
            display_prompt += f" [{default}]"
        display_prompt += ": "
        
        response = input(display_prompt).strip()
        
        if not response and default:
            return default
        elif not response and required:
            print_error("Input is required. Please try again.")
            continue
        else:
            return response

def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def move_cursor(x: int, y: int) -> None:
    """
    Move cursor to specified position.

    Args:
        x (int): Column position.
        y (int): Row position.
    """
    print(f"\033[{y};{x}H", end='')

# Alias for backward compatibility
@DeprecationWarning
def printprogress(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """Legacy function name for print_progress_bar."""
    print_progress_bar(iteration, total, prefix, suffix, decimals, length, fill, printEnd)