<#
===============================================================================
Module: compare_directories.ps1
Description:
  Windows PowerShell wrapper for the Python script 'compare_directories.py'.
  This script determines its own directory and calls the Python script located
  in the sibling 'python' directory, passing all provided arguments.
  
Usage:
  .\compare_directories.ps1 [arguments...]
===============================================================================
#>

# Get the directory of the current script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Construct the full path to the Python script
$pythonScript = Join-Path $scriptDir '..\python\compare_directories.py'

# Execute the Python script with all provided arguments
python $pythonScript $args
