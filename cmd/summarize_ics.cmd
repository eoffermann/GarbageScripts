@echo off
REM =============================================================================
REM Module: summarize_ics.cmd
REM Description:
REM   Windows CMD wrapper for the Python script 'summarize_ics.py'.
REM   This script determines its own directory using %~dp0 and calls the Python 
REM   script in the sibling 'python' directory, passing all provided arguments.
REM 
REM Usage:
REM   summarize_ics [arguments...]
REM =============================================================================
set FILENAME=summarize_ics

REM %~dp0 returns the drive letter and path of the running script.
set SCRIPT_DIR=%~dp0
REM Construct the full path to the Python script.
set PYTHON_SCRIPT=%SCRIPT_DIR%\..\python\%FILENAME%.py

REM Call the Python script with all command-line arguments.
python "%PYTHON_SCRIPT%" %*
