#!/usr/bin/env python3
"""
Launcher script for Five in a Row (Gomoku) game.
This script ensures proper paths are set before launching the game.
"""

import os
import sys
import platform
import subprocess

def run_game():
    """Set up environment and launch the game."""
    # Get the script directory which should be the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Make sure we're in the project root by checking for src directory
    if not os.path.exists(os.path.join(project_root, 'src')):
        print("Warning: Could not locate src directory. File paths might be incorrect.")
    
    # Print system information
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Project root: {project_root}")
    
    # Make sure lib directory exists
    lib_dir = os.path.join(project_root, 'lib')
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)
        print(f"Created lib directory: {lib_dir}")
    
    # Copy the compiled library to lib directory
    library_filename = None
    if platform.system() == 'Darwin':  # macOS
        library_filename = 'libgomoku.dylib'
    elif platform.system() == 'Linux':
        library_filename = 'libgomoku.so'
    elif platform.system() == 'Windows':
        library_filename = 'gomoku.dll'
    else:
        print(f"Warning: Unsupported platform {platform.system()}")
    
    if library_filename:
        build_lib_path = os.path.join(project_root, 'build', library_filename)
        lib_path = os.path.join(lib_dir, library_filename)
        
        # Check if library exists in build directory
        if os.path.exists(build_lib_path):
            # Copy to lib directory
            import shutil
            shutil.copyfile(build_lib_path, lib_path)
            print(f"Copied library from {build_lib_path} to {lib_path}")
        else:
            print(f"Warning: Library not found at {build_lib_path}")
    
    # Run resource setup script
    resource_setup_script = os.path.join(project_root, 'src', 'frontend', 'setup_resources.py')
    if os.path.exists(resource_setup_script):
        print("\n=== Setting up resources ===")
        subprocess.call([sys.executable, resource_setup_script])
    
    # Launch the game
    game_script = os.path.join(project_root, 'src', 'frontend', 'gomoku_app.py')
    if os.path.exists(game_script):
        print("\n=== Launching the game ===")
        os.environ['PYTHONPATH'] = project_root  # Add project root to Python path
        subprocess.call([sys.executable, game_script])
    else:
        print(f"Error: Game script not found at {game_script}")

if __name__ == "__main__":
    run_game()
