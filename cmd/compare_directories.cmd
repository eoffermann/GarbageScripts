@echo off
REM =============================================================================
REM Module: compare_directories.cmd
REM Description:
REM   Windows CMD wrapper for the Python script 'compare_directories.py'.
REM   This script determines its own directory using %~dp0 and calls the Python 
REM   script in the sibling 'python' directory, passing all provided arguments.
REM 
REM Usage:
REM   compare_directories [arguments...]
REM =============================================================================

REM %~dp0 returns the drive letter and path of the running script.
set SCRIPT_DIR=%~dp0
REM Construct the full path to the Python script.
set PYTHON_SCRIPT=%SCRIPT_DIR%\..\python\compare_directories.py

REM Call the Python script with all command-line arguments.
python "%PYTHON_SCRIPT%" %*
