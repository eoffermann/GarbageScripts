#!/usr/bin/env python
"""
File: compare_directories.py
Description: This script recursively scans two directory hierarchies and compares their files by computing SHA-256 hashes.
             It identifies files that exist in the reference directory but not in the main directory and vice versa,
             matching files by their content (hash) rather than their names. The output is a JSON file containing statistics
             and tables showing correspondences between the two hierarchies.
Usage:
    python compare_directories.py -p <main_directory> -r <reference_directory> -o <output_json> [-v]
Flags:
    -p, --path       Main path to a directory whose contents will be analyzed.
    -r, --reference  Reference path to a directory to compare files with.
    -o, --output     Output JSON file path for the results.
    -v, --verbose    (Optional) Enable verbose output to stdout.
"""

import os
import argparse
import hashlib
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

def compute_file_hash(file_path: str, buffer_size: int = 65536) -> Optional[str]:
    """Compute SHA-256 hash for a given file.
    
    Reads the file in binary mode in chunks to efficiently handle large files.
    
    Args:
        file_path (str): The absolute path to the file.
        buffer_size (int, optional): The size (in bytes) of the chunk to read at a time. Defaults to 65536.
    
    Returns:
        Optional[str]: The hexadecimal SHA-256 hash of the file, or None if an error occurs.
    """
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read file in chunks
            while chunk := f.read(buffer_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error computing hash for file {file_path}: {e}")
        return None

def scan_directory(root_path: str, verbose: bool = False) -> Dict[str, List[str]]:
    """Recursively scan a directory, compute hashes for each file, and build a mapping from file hash to file paths.
    
    Args:
        root_path (str): The directory path to scan.
        verbose (bool, optional): If True, logs additional information about the scanning process. Defaults to False.
    
    Returns:
        Dict[str, List[str]]: A dictionary where each key is a file hash and the value is a list of file paths (relative to root_path)
                              having that hash.
    """
    hash_map: Dict[str, List[str]] = {}
    files_to_process = []

    # Walk through directory and gather all file paths
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(full_path, root_path)
            files_to_process.append((full_path, relative_path))
    
    if verbose:
        logging.info(f"Found {len(files_to_process)} files in {root_path}")

    # Use ThreadPoolExecutor to compute file hashes concurrently
    with ThreadPoolExecutor() as executor:
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
    """Parse command-line arguments, scan the main and reference directories, compare them by file hash, and write results to a JSON file."""
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
    
    args = parser.parse_args()
    
    # Set up logging based on verbosity flag
    logging_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=logging_level, format='%(levelname)s: %(message)s')
    
    # Resolve absolute paths
    main_dir = os.path.abspath(args.path)
    ref_dir = os.path.abspath(args.reference)
    
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
        logging.info(f"Statistics: {results['stats']}")
    
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
