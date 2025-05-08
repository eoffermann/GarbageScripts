#!/usr/bin/env python3
"""
deduplicate.py

This script scans a directory recursively to perform a deduplication analysis of files. It
calculates a checksum for the first portion of each file (using the first 512 bytes) along with
the file length to group potential duplicates. For groups with more than one file, the script
increments the compared portion (the “depth”) of the file until either the entire file has been
read or until a difference is detected among files. Only groups with duplicate files (i.e. more
than one file per group) are written to the output JSON file.

Usage:
    python deduplicate.py -d <directory> -o <output_json_file>
"""

import os
import sys
import json
import argparse
import hashlib
from typing import List, Dict, Tuple

# Constants for initial and extended chunk sizes
INITIAL_CHUNK_SIZE: int = 512
EXTEND_CHUNK_SIZE: int = 512


def compute_checksum(file_path: str, num_bytes: int) -> str:
    """Compute a checksum of the first `num_bytes` bytes of a file.

    Args:
        file_path (str): The path to the file.
        num_bytes (int): The number of bytes to read from the start of the file.

    Returns:
        str: The hexadecimal digest of the computed MD5 checksum.
    """
    md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            data = f.read(num_bytes)
            md5.update(data)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return ""
    return md5.hexdigest()


def extend_common_prefix(paths: List[str], current_depth: int, file_size: int) -> int:
    """Extend the common prefix depth for a group of files.

    Starting at the given current_depth, this function reads each file in blocks (using
    EXTEND_CHUNK_SIZE) and compares the blocks across all files. If the blocks are identical,
    the function increments the depth by the block length; if differences are found, it
    determines the exact number of matching bytes in the current block and stops extending.

    Args:
        paths (List[str]): The list of file paths to compare.
        current_depth (int): The current number of bytes known to be identical.
        file_size (int): The total size of each file (all files have the same size in a group).

    Returns:
        int: The new common prefix length in bytes among all files.
    """
    new_depth = current_depth
    # Continue until we reach the file size.
    while new_depth < file_size:
        # Read the next chunk from each file
        chunks = []
        for path in paths:
            try:
                with open(path, "rb") as f:
                    f.seek(new_depth)
                    chunk = f.read(EXTEND_CHUNK_SIZE)
                    chunks.append(chunk)
            except Exception as e:
                print(f"Error reading {path}: {e}", file=sys.stderr)
                chunks.append(b"")
        
        # If any chunk is empty (could be due to reading error), break.
        if any(len(chunk) == 0 for chunk in chunks):
            break

        # Check if all chunks are identical
        first_chunk = chunks[0]
        if all(chunk == first_chunk for chunk in chunks):
            # All chunks are the same; extend new_depth by the size of this chunk.
            new_depth += len(first_chunk)
            # If the chunk was short (end of file reached), then break out.
            if len(first_chunk) < EXTEND_CHUNK_SIZE:
                break
        else:
            # If chunks differ, compare byte-by-byte to count common matching bytes.
            match_in_chunk = len(first_chunk)
            for i in range(len(first_chunk)):
                # Check the byte in each chunk; if any difference, update match count.
                current_byte = first_chunk[i]
                for other_chunk in chunks[1:]:
                    # If we run out of bytes in any chunk, adjust the match length.
                    if i >= len(other_chunk) or other_chunk[i] != current_byte:
                        match_in_chunk = i
                        break
                else:
                    # Continue if inner loop did not break
                    continue
                # Break out of the outer loop if a difference was found.
                break

            new_depth += match_in_chunk
            break  # Stop extending as soon as a difference is found.
    return new_depth


def scan_directory(directory: str) -> Dict[Tuple[str, int], Dict]:
    """Recursively scan a directory to group files based on an initial checksum and file length.

    For every file found under the directory, this function calculates a checksum of the first
    INITIAL_CHUNK_SIZE bytes (or less if the file is smaller) and groups files by the tuple
    (checksum, file_size). Each group stores the common depth (initially the number of bytes read)
    and the list of file paths that share that key.

    Args:
        directory (str): The root directory to scan.

    Returns:
        Dict[Tuple[str, int], Dict]: A dictionary where keys are tuples (checksum, file_size) and
            values are dictionaries with keys:
                - "depth": int, the number of bytes used in the checksum calculation.
                - "paths": List[str], a list of file paths that have that checksum and size.
    """
    groups: Dict[Tuple[str, int], Dict] = {}
    for root, dirs, files in os.walk(directory):
        print(f"Scanning: {root}")
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_size = os.path.getsize(file_path)
            except Exception as e:
                print(f"Error getting size of {file_path}: {e}", file=sys.stderr)
                continue

            # Determine how many bytes to read (if file is smaller than INITIAL_CHUNK_SIZE)
            depth = min(file_size, INITIAL_CHUNK_SIZE)
            checksum = compute_checksum(file_path, depth)
            if checksum == "":
                continue  # Skip file if checksum could not be computed

            key = (checksum, file_size)
            if key not in groups:
                groups[key] = {"depth": depth, "paths": [file_path]}
            else:
                print(f"   Possible match: {file_path}")
                groups[key]["paths"].append(file_path)
    return groups


def update_duplicate_groups(groups: Dict[Tuple[str, int], Dict]) -> List[Dict]:
    """Extend the comparison for groups with potential duplicates and filter out unique entries.

    For groups with more than one file, this function extends the comparison (the depth) by
    reading further parts of the file until the end of file is reached or a difference is found.
    After extension, any group containing only one file is discarded.

    Args:
        groups (Dict[Tuple[str, int], Dict]): The initial grouping of files from scan_directory.

    Returns:
        List[Dict]: A list of dictionaries. Each dictionary represents a group with duplicate files,
            including the initial checksum, file size, common prefix (depth), and list of paths.
    """
    duplicates = []
    for key, group in groups.items():
        paths = group["paths"]
        file_size = key[1]
        # Only process groups with more than one file.
        if len(paths) < 2:
            continue

        current_depth = group["depth"]
        # If the current compared depth does not cover the full file, extend the comparison.
        if current_depth < file_size:
            new_depth = extend_common_prefix(paths, current_depth, file_size)
            group["depth"] = new_depth

        # Only keep groups with more than one file.
        if len(group["paths"]) > 1:
            duplicate_group = {
                "initial_checksum": key[0],
                "file_size": file_size,
                "common_prefix": group["depth"],
                "files": paths,
            }
            duplicates.append(duplicate_group)
    return duplicates


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Analyze duplicate files by computing partial and extended checksums."
    )
    parser.add_argument(
        "-d", "--dir", required=True, type=str, help="Directory to examine recursively."
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=str,
        help="JSON file where deduplication analysis results will be stored.",
    )
    return parser.parse_args()


def main() -> None:
    """The main function that orchestrates the deduplication analysis and writes the output JSON."""
    args = parse_arguments()

    if not os.path.isdir(args.dir):
        print(f"Error: Directory '{args.dir}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    # Scan directory and group files by initial checksum and file size.
    groups = scan_directory(args.dir)
    # Process groups to extend checksum comparison and remove groups with only one file.
    duplicates = update_duplicate_groups(groups)

    try:
        with open(args.output, "w") as outfile:
            json.dump({"duplicates": duplicates}, outfile, indent=4)
        print(f"Deduplication analysis complete. Results written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file {args.output}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
