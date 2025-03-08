@echo off
REM =============================================================================
REM Module: rename_uuid.cmd
REM Description:
REM   Windows CMD wrapper for the Python script 'rename_uuid.py'.
REM   This script determines its own directory using %~dp0 and calls the Python 
REM   script in the sibling 'python' directory, passing all provided arguments.
REM 
REM Usage:
REM   rename_uuid [arguments...]
REM =============================================================================

set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%\..\python\rename_uuid.py

python "%PYTHON_SCRIPT%" %*
