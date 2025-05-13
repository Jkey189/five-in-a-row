# Five in a Row (Gomoku)

A fully-featured implementation of the classic game "Five in a Row" (Gomoku) with a PyQt5 frontend and C++ backend using the alpha-beta pruning algorithm.

## Features

- Beautiful PyQt5 GUI with modern interface
- Strong AI opponent using alpha-beta pruning algorithm with adjustable difficulty
- Multiple difficulty levels (Easy, Medium, Hard)
- Undo move functionality
- Game saving and loading
- Game timer
- Game statistics tracking
- Cross-platform compatibility (Windows, macOS, Linux)

## Requirements

- C++ compiler with C++14 support
- CMake 3.10 or higher
- Python 3.6 or higher
- PyQt5

## Quick Installation

The easiest way to install and run the game is to use our setup script:

```bash
# On macOS/Linux
python3 setup.py

# On Windows
python setup.py
```

This comprehensive setup will:
1. Check for required tools and dependencies
2. Install needed Python packages
3. Build the C++ backend optimized for your platform
4. Set up all game resources
5. Create launchers for your platform
6. Create a desktop shortcut for convenient access

You can customize the installation with these options:
```bash
python3 setup.py --no-deps      # Skip installing Python dependencies
python3 setup.py --no-build     # Skip building the C++ backend
python3 setup.py --no-shortcut  # Skip creating desktop shortcut
python3 setup.py --no-cleanup   # Skip cleanup step
```

## Manual Installation

### Install Dependencies

First, install Python and PyQt5:

```bash
# For pip users
pip install PyQt5 pillow scipy
```

or

```bash
# For conda users
conda install -c anaconda pyqt pillow scipy
```

### Build the C++ Backend

On macOS/Linux:

```bash
chmod +x build.sh
./build.sh
```

On Windows:

```cmd
build.bat
```

## Running the Game

After installation, run the game with:

```bash
# On macOS/Linux
./play_gomoku.sh

# On Windows
play_gomoku.bat
```

Or directly use the Python launcher:

```bash
python3 play_gomoku.py
```

## How to Play

1. The player uses black stones, and the AI uses white stones.
2. Click on the board to place your stone.
3. The first player to get exactly five stones in a row (horizontally, vertically, or diagonally) wins the game.
4. Click "New Game" to restart at any time.

## Troubleshooting

### Diagnostics Tool

If you encounter any issues, run the diagnostics tool to automatically identify and fix common problems:

```bash
# On macOS/Linux
python3 diagnostics.py

# On Windows
python diagnostics.py
```

This tool will check for:
- Python version compatibility
- Required Python packages
- C++ library availability and loading
- Game resources (icons and settings)
- File permissions
- And offer to fix any issues detected

### Library Loading Issues

If you see errors like "Cannot load library" or "Library not found":

1. Verify that the library is built correctly:
   ```bash
   # Check if library exists
   ls -la lib/libgomoku.dylib   # On macOS
   ls -la lib/libgomoku.so      # On Linux
   dir lib\gomoku.dll           # On Windows
   ```

2. Rebuild the library:
   ```bash
   # On macOS/Linux
   ./build.sh
   
   # On Windows
   build.bat
   ```

3. Run the resource setup script:
   ```bash
   python3 src/frontend/setup_resources.py
   ```

4. Use the launcher script which handles library paths automatically:
   ```bash
   python3 play_gomoku.py
   ```

### Missing Resources

If you encounter errors about missing icons:

1. Make sure the resources directory exists and contains the required files:
   ```bash
   # Check resources directory
   ls -la resources/
   ```

2. Run the setup_resources.py script to locate or generate missing resources:
   ```bash
   python3 src/frontend/setup_resources.py
   ```

3. If the icon is still missing, you can manually generate it:
   ```bash
   # Generate game icon
   python3 src/frontend/create_icon.py
   ```

### Platform-Specific Issues

#### Windows

- Ensure you have a C++ compiler installed (Visual Studio or MinGW-w64)
- Make sure CMake is in your PATH
- Check that Python is in your PATH

#### macOS

- Install Xcode Command Line Tools if you encounter compiler errors:
  ```bash
  xcode-select --install
  ```
- If you see a security warning when launching the game, go to System Settings > Privacy & Security and allow the app to run

#### Linux

- Install required development packages:
  ```bash
  # On Debian/Ubuntu
  sudo apt-get install build-essential cmake python3-dev python3-pyqt5
  
  # On Fedora
  sudo dnf install gcc-c++ cmake python3-devel python3-pyqt5
  ```

## Project Structure

- `src/backend/` - C++ backend with alpha-beta pruning algorithm
- `src/frontend/` - PyQt5 GUI
- `lib/` - Compiled shared library
- `resources/` - Game resources
- `play_gomoku.py` - Main launcher script
- `install.py` - Installation and setup script

## License

MIT License
