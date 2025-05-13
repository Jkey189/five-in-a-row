@echo off
REM Launcher script for Five in a Row (Gomoku) game

echo Starting Five in a Row (Gomoku)...
echo.

REM Make sure we're in the right directory
cd /d "%~dp0"

REM Set up Python path environment variable
set PYTHONPATH=%CD%

REM Check if Python is available
python --version 2>NUL
if %ERRORLEVEL% neq 0 (
    echo Python not found in PATH. Please make sure Python is installed.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

REM Run the launcher script
python play_gomoku.py

REM If the game exited with an error, wait for user input
if %ERRORLEVEL% neq 0 (
    echo.
    echo The game exited with an error. Check the output above for details.
    echo Press any key to exit...
    pause > nul
)
