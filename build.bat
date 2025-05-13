@echo off
REM Five in a Row (Gomoku) Windows Build Script

echo Building Five in a Row (Gomoku) on Windows...

REM Get script directory 
set "SCRIPT_DIR=%~dp0"

REM Create build directory if it doesn't exist
if not exist "%SCRIPT_DIR%build" mkdir "%SCRIPT_DIR%build"

REM Create lib directory if it doesn't exist
if not exist "%SCRIPT_DIR%lib" mkdir "%SCRIPT_DIR%lib"

REM Navigate to the build directory
cd /d "%SCRIPT_DIR%build"

REM Configure with CMake
echo Configuring with CMake...
cmake ..
if %ERRORLEVEL% neq 0 (
    echo CMake configuration failed! Error code: %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

REM Build the project
echo Building...
cmake --build . --config Release
if %ERRORLEVEL% neq 0 (
    echo Build failed! Error code: %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

REM Copy the library to lib directory
if exist Release\gomoku.dll (
    copy Release\gomoku.dll "%SCRIPT_DIR%lib\"
    echo Copied gomoku.dll to lib directory
) else if exist gomoku.dll (
    copy gomoku.dll "%SCRIPT_DIR%lib\"
    echo Copied gomoku.dll to lib directory
) else (
    echo Warning: gomoku.dll not found in build directory
)

echo Build completed successfully!
cd /d "%SCRIPT_DIR%"
