# Gomoku Cross-Platform Improvements

This document summarizes the improvements made to ensure the Five in a Row (Gomoku) game works consistently across Windows, macOS, and Linux platforms.

## Core Improvements

### 1. Library Loading Mechanism
- Enhanced to search for the library in multiple possible locations
- Better error reporting and fallback mechanisms
- Platform-specific library path handling (DLL, .so, .dylib)

### 2. Resource Management
- Centralized resource handling
- Support for symbolic links when appropriate
- Multiple resource directory scanning
- Automatic resource generation when missing

### 3. Build System
- Improved build scripts for all platforms
- Consistent library output locations
- Automatic copying of built libraries

### 4. Installation & Setup
- Created a comprehensive setup.py installation script
- Cross-platform launcher scripts (play_gomoku.py, play_gomoku.sh, play_gomoku.bat)
- Platform-specific desktop shortcut creation

### 5. Environment Validation
- Added validation of library and resource availability
- Runtime error handling and recovery
- Warnings for missing components

### 6. Troubleshooting
- Created diagnostics.py for automatic issue detection and resolution
- Improved error messages with actionable suggestions
- Enhanced logging for debugging purposes

## Files Created/Modified

### New Files
1. `setup.py` - Cross-platform installation script
2. `diagnostics.py` - Troubleshooting and repair tool
3. `play_gomoku.sh` - Unix shell launcher
4. `play_gomoku.bat` - Windows batch launcher

### Modified Files
1. `src/frontend/gomoku_app.py` - Enhanced library loading and environment validation
2. `src/frontend/setup_resources.py` - Improved resource discovery and setup
3. `src/frontend/test_backend.py` - Updated library loading mechanism
4. `play_gomoku.py` - Better path handling and resource setup
5. `build.sh` - Improved build process and library placement
6. `build.bat` - Enhanced Windows build script with error handling
7. `README.md` - Updated documentation and troubleshooting guides

## Platform-Specific Considerations

### Windows
- Support for both Visual Studio and MinGW compilers
- Proper handling of Windows paths with spaces
- Registry-free installation (portable application)
- COM-based shortcut creation

### macOS
- Support for universal binaries
- Proper dylib handling and loading
- Resources in standard macOS locations
- AppleScript for desktop integration

### Linux
- Compatibility with common Linux distributions
- Support for XDG desktop standards
- Appropriate file permissions handling
- Package-free installation
