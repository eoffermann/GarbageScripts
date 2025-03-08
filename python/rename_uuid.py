#!/usr/bin/env python3
"""
A script to recursively rename all files and directories within a given path either to UUID4 names or to a random sequence of 4 English words.
For files, the original extension is preserved.

Usage:
    python rename_uuid_words.py -p /path/to/directory [--words]
    
Options:
    -p, --path     Path to the directory to process.
    -w, --words    Rename using a random sequence of 4 English words instead of UUID4.

Dependencies:
    - Python 3.x
    - Internet connection (if using word-based renaming, as it downloads a word list)
"""

import argparse
import os
import uuid
import random
import urllib.request
from typing import List, Callable, NoReturn

# URL to download a word list from.
WORD_LIST_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"

def generate_uuid_name(ext: str = "") -> str:
    """Generate a new UUID4-based name with an optional file extension.

    Args:
        ext (str, optional): The file extension (including the dot) to append. Defaults to "".

    Returns:
        str: A string combining the UUID and the extension.
    """
    new_uuid = str(uuid.uuid4())
    return f"{new_uuid}{ext}" if ext else new_uuid

def generate_words_name(word_list: List[str], ext: str = "") -> str:
    """Generate a new name composed of a random sequence of 4 English words, joined by dashes.
    The file extension is preserved if provided.

    Args:
        word_list (List[str]): List of English words to sample from.
        ext (str, optional): The file extension (including the dot) to append. Defaults to "".

    Returns:
        str: A string in the format "word1-word2-word3-word4" with the extension appended if provided.
    """
    words = random.sample(word_list, 4)
    name = "-".join(words)
    return f"{name}{ext}" if ext else name

def get_word_list(url: str) -> List[str]:
    """Download a list of English words from the given URL and return it as a list.

    Args:
        url (str): The URL to download the word list from.

    Returns:
        List[str]: A list of English words.

    Raises:
        SystemExit: If an error occurs during the download.
    """
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
        words = [line.strip() for line in data.splitlines() if line.strip()]
        return words
    except Exception as e:
        print(f"Error downloading word list: {e}")
        exit(1)  # Exit with an error code

def rename_files_and_directories(root_path: str, name_generator: Callable[[str], str]) -> None:
    """Recursively rename all files and directories in the given root path using the provided naming function.

    The renaming is performed in a bottom-up manner (via os.walk with topdown=False)
    to avoid issues with renaming directories before their contents.

    Args:
        root_path (str): The root directory where renaming begins.
        name_generator (Callable[[str], str]): A function that generates a new name given an optional extension.

    Returns:
        None
    """
    for current_dir, dirs, files in os.walk(root_path, topdown=False):
        # Rename files first, preserving extensions.
        for filename in files:
            old_path = os.path.join(current_dir, filename)
            _, ext = os.path.splitext(filename)
            new_name = name_generator(ext)
            new_path = os.path.join(current_dir, new_name)
            print(f"Renaming file: {old_path} -> {new_path}")
            os.rename(old_path, new_path)
        
        # Rename directories (directories do not have extensions).
        for directory in dirs:
            old_path = os.path.join(current_dir, directory)
            new_name = name_generator("")
            new_path = os.path.join(current_dir, new_name)
            print(f"Renaming directory: {old_path} -> {new_path}")
            os.rename(old_path, new_path)

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Recursively rename all files and directories with UUID4 names or a random sequence of 4 English words."
    )
    parser.add_argument(
        "-p", "--path",
        required=True,
        type=str,
        help="Path to the directory to rename files and directories within."
    )
    parser.add_argument(
        "-w", "--words",
        action="store_true",
        help="Rename using a random sequence of 4 English words instead of UUID4."
    )
    return parser.parse_args()

def main() -> NoReturn:
    """Main function to execute the renaming process.

    Validates the input path, optionally downloads a word list if words mode is enabled,
    and calls the renaming function.
    """
    args = parse_arguments()

    # Validate that the provided path exists and is a directory.
    if not os.path.exists(args.path):
        print(f"Error: The provided path does not exist: {args.path}")
        exit(1)
    if not os.path.isdir(args.path):
        print(f"Error: The provided path is not a directory: {args.path}")
        exit(1)

    # Determine which naming function to use.
    if args.words:
        print("Downloading word list...")
        word_list = get_word_list(WORD_LIST_URL)
        name_generator = lambda ext: generate_words_name(word_list, ext)  # Use word-based naming
    else:
        name_generator = generate_uuid_name  # Use UUID-based naming

    rename_files_and_directories(args.path, name_generator)
    print("Renaming completed successfully.")

if __name__ == "__main__":
    main()
