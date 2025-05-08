#!/usr/bin/env bash
# =============================================================================
# Module: summarize_ics
# Description:
#   Bash wrapper for the Python script 'summarize_ics.py'.
#   This script determines its own directory and calls the Python script located
#   in the sibling 'python' directory, passing all provided arguments.
#
# Usage:
#   ./summarize_ics [arguments...]
#
# =============================================================================
FILENAME="summarize_ics"

# Get the directory of this wrapper script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Construct the full path to the Python script (assumed to be one level up in 'python')
PYTHON_SCRIPT="$SCRIPT_DIR/../python/$FILENAME.py"

# Execute the Python script with all passed arguments
python "$PYTHON_SCRIPT" "$@"
