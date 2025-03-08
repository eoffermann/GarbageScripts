#!/usr/bin/env python
"""
File: compare_directories.py
Description: This script recursively scans two directory hierarchies and compares their files by computing SHA-256 hashes.
             It identifies files that exist in the reference directory but not in the main directory and vice versa,
             matching files by their content (hash) rather than their names. The output is a JSON file containing statistics
             and tables showing correspondences between the two hierarchies.

Usage:
    python compare_directories.py -p <main_directory> -r <reference_directory> -o <output_json> [-v] [--threads <num_threads>]

Flags:
    -p, --path       Main path to a directory whose contents will be analyzed.
    -r, --reference  Reference path to a directory to compare files with.
    -o, --output     Output JSON file path for the results.
    -v, --verbose    (Optional) Enable verbose output to stdout.
    --threads        (Optional) Number of threads to use for concurrent file hashing. Defaults to the executor's default.

TODO:
    - Consider adding a progress bar (e.g., using tqdm) for large directory scans.
    - Implement a CSV output option for human-readable reports.
    - Allow configurable hash algorithms (e.g., MD5, SHA-256).
    - Enhance error handling for inaccessible files or directories.
    - Explore async I/O for further performance improvements.
"""

import os
import argparse
import hashlib
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple


def compute_file_hash(file_path: str, buffer_size: int = 65536) -> Optional[str]:
    """
    Compute SHA-256 hash for a given file.

    This function reads the file in binary mode in chunks to efficiently handle large files.

    Args:
        file_path (str): The absolute path to the file.
        buffer_size (int, optional): The size (in bytes) of the chunk to read at a time. Defaults to 65536.

    Returns:
        Optional[str]: The hexadecimal SHA-256 hash of the file, or None if an error occurs.

    TODO:
        - Add support for configurable hash algorithms.
        - Consider asynchronous file reading for potential performance improvements.
    """
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(buffer_size):
                hasher.update(chunk)
        logging.debug(f"Computed hash for {file_path}")
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error computing hash for file {file_path}: {e}")
        return None


def scan_directory(root_path: str, verbose: bool = False) -> Dict[str, List[str]]:
    """
    Recursively scan a directory using os.scandir(), compute hashes for each file, and build a mapping
    from file hash to file paths.

    This implementation uses a recursive helper function and os.scandir() for improved performance
    over os.walk() on large directories.

    Args:
        root_path (str): The directory path to scan.
        verbose (bool, optional): If True, logs additional information about the scanning process. Defaults to False.

    Returns:
        Dict[str, List[str]]: A dictionary where each key is a file hash and the value is a list of file paths
                              (relative to root_path) having that hash.

    TODO:
        - Enhance error handling for directories with permission issues.
        - Consider yielding file paths to reduce memory usage in extremely large directories.
    """
    hash_map: Dict[str, List[str]] = {}
    files_to_process: List[Tuple[str, str]] = []

    def recursive_scan(current_path: str) -> None:
        """
        Recursively scan the given directory using os.scandir().

        Args:
            current_path (str): The current directory path being scanned.

        TODO:
            - Handle symlinks or special files if needed.
        """
        try:
            with os.scandir(current_path) as it:
                for entry in it:
                    if entry.is_file(follow_symlinks=False):
                        full_path = entry.path
                        relative_path = os.path.relpath(full_path, root_path)
                        files_to_process.append((full_path, relative_path))
                    elif entry.is_dir(follow_symlinks=False):
                        recursive_scan(entry.path)
        except Exception as e:
            logging.error(f"Error scanning directory {current_path}: {e}")
            # TODO: Handle specific errors (e.g., permission issues) more gracefully.

    recursive_scan(root_path)

    if verbose:
        logging.info(f"Found {len(files_to_process)} files in {root_path}")

    # Use a configurable number of threads; if not provided, ThreadPoolExecutor uses its default settings.
    num_threads: Optional[int] = None  # TODO: Allow this to be configurable via command-line argument if needed.
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_file = {
            executor.submit(compute_file_hash, full_path): rel_path
            for full_path, rel_path in files_to_process
        }
        for future in as_completed(future_to_file):
            rel_path = future_to_file[future]
            file_hash = future.result()
            if file_hash is not None:
                hash_map.setdefault(file_hash, []).append(rel_path)
            else:
                if verbose:
                    logging.warning(f"Failed to compute hash for {rel_path}")
    return hash_map


def main() -> None:
    """
    Parse command-line arguments, scan the main and reference directories, compare them by file hash,
    and write the results to a JSON file.

    This function sets up logging, resolves directory paths, compares file hash maps from both directories,
    and outputs the results along with statistical information.

    TODO:
        - Add a command-line argument to explicitly configure the thread pool size.
        - Consider adding a progress bar to visualize file processing.
        - Evaluate adding a CSV output option for different user preferences.
    """
    parser = argparse.ArgumentParser(
        description="Compare two directory hierarchies by file content (hashes)."
    )
    parser.add_argument('-p', '--path', required=True,
                        help='Main path to a directory to analyze.')
    parser.add_argument('-r', '--reference', required=True,
                        help='Reference path to a directory to compare files with.')
    parser.add_argument('-o', '--output', required=True,
                        help='Output JSON file to write scan results.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output.')
    parser.add_argument('--threads', type=int, default=None,
                        help="Number of threads to use for concurrent file hashing. Defaults to the executor's default.")

    args = parser.parse_args()

    # Set up logging based on the verbosity flag
    logging_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=logging_level, format='%(levelname)s: %(message)s')

    # Resolve absolute paths
    main_dir: str = os.path.abspath(args.path)
    ref_dir: str = os.path.abspath(args.reference)

    if args.verbose:
        logging.info(f"Main directory: {main_dir}")
        logging.info(f"Reference directory: {ref_dir}")

    # Scan both directories and compute file hash mappings
    main_hashes = scan_directory(main_dir, args.verbose)
    ref_hashes = scan_directory(ref_dir, args.verbose)

    # Create sets of hashes for comparison
    main_hash_set = set(main_hashes.keys())
    ref_hash_set = set(ref_hashes.keys())

    common_hashes = main_hash_set.intersection(ref_hash_set)
    missing_in_main = {h: ref_hashes[h] for h in ref_hash_set - main_hash_set}
    missing_in_reference = {h: main_hashes[h] for h in main_hash_set - ref_hash_set}

    # Build the results dictionary for JSON output
    results = {
        "stats": {
            "total_main_files": sum(len(v) for v in main_hashes.values()),
            "total_reference_files": sum(len(v) for v in ref_hashes.values()),
            "unique_hashes_in_main": len(main_hashes),
            "unique_hashes_in_reference": len(ref_hashes),
            "common_hashes_count": len(common_hashes),
            "missing_in_main_count": sum(len(v) for v in missing_in_main.values()),
            "missing_in_reference_count": sum(len(v) for v in missing_in_reference.values()),
        },
        "common_files": [
            {
                "hash": h,
                "main_files": main_hashes[h],
                "reference_files": ref_hashes[h]
            }
            for h in common_hashes
        ],
        "missing_in_main": [
            {
                "hash": h,
                "reference_files": ref_hashes[h]
            }
            for h in missing_in_main
        ],
        "missing_in_reference": [
            {
                "hash": h,
                "main_files": main_hashes[h]
            }
            for h in missing_in_reference
        ]
    }

    if args.verbose:
        logging.info("Comparison complete. Writing output JSON file.")
        logging.debug(f"Statistics: {results['stats']}")

    # Write the results to the specified JSON output file
    try:
        with open(args.output, 'w', encoding='utf-8') as outfile:
            json.dump(results, outfile, indent=4)
        if args.verbose:
            logging.info(f"Results successfully written to {args.output}")
    except Exception as e:
        logging.error(f"Failed to write output file {args.output}: {e}")


if __name__ == '__main__':
    main()
