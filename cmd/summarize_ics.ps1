<#
===============================================================================
Module: summarize_ics.ps1
Description:
  Windows PowerShell wrapper for the Python script 'summarize_ics.py'.
  This script determines its own directory and calls the Python script located
  in the sibling 'python' directory, passing all provided arguments.
  
Usage:
  .\summarize_ics.ps1 [arguments...]
===============================================================================
#>

$filename="summarize_ics"

# Get the directory of the current script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Construct the full path to the Python script
$pythonScript = Join-Path (Join-Path $scriptDir "..\python") "$filename.py"

# Execute the Python script with all provided arguments
python $pythonScript $args
