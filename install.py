#!/usr/bin/env python3
"""
Installer for Five in a Row (Gomoku).
This script sets up the game environment regardless of the platform.
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse

def print_section(title):
    """Print a section title in a formatted way."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def run_command(command, cwd=None):
    """Run a command and print its output."""
    print(f"> {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False

def get_project_root():
    """Get the project root directory."""
    return os.path.dirname(os.path.abspath(__file__))

def build_backend():
    """Build the C++ backend for the current platform."""
    print_section("Building C++ Backend")
    
    # Get project root
    project_root = get_project_root()
    print(f"Project root: {project_root}")
    
    # Create build and lib directories if they don't exist
    build_dir = os.path.join(project_root, 'build')
    lib_dir = os.path.join(project_root, 'lib')
    
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(lib_dir, exist_ok=True)
    
    # Determine platform and build
    if platform.system() == "Windows":
        print("Building on Windows...")
        
        # First check if Visual Studio is available
        if shutil.which("cl.exe"):
            print("Using Visual Studio for building")
            return run_command("build.bat", cwd=project_root)
        else:
            # Try MinGW
            print("Visual Studio compiler not found, trying MinGW...")
            return run_command("cmake -G \"MinGW Makefiles\" .. && cmake --build .", cwd=build_dir)
    else:
        # Unix-like systems (Linux, macOS)
        print(f"Building on {platform.system()}...")
        
        # Make build script executable
        try:
            build_script = os.path.join(project_root, 'build.sh')
            os.chmod(build_script, 0o755)
            print("Made build.sh executable")
        except Exception as e:
            print(f"Warning: Could not make build.sh executable: {e}")
        
        # Run the build script
        return run_command('./build.sh', cwd=project_root)

def setup_python_environment():
    """Set up the Python environment."""
    print_section("Setting Up Python Environment")
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Python version: {python_version}")
    
    if int(python_version.split('.')[0]) < 3 or (int(python_version.split('.')[0]) == 3 and int(python_version.split('.')[1]) < 6):
        print("Warning: This application requires Python 3.6 or higher")
    
    # Install required packages
    print("Installing required Python packages...")
    packages = ["PyQt5", "pillow", "scipy"]
    
    for package in packages:
        print(f"Installing {package}...")
        run_command(f"{sys.executable} -m pip install {package}")
    
    return True

def setup_resources():
    """Set up game resources."""
    print_section("Setting Up Game Resources")
    
    # Get project root
    project_root = get_project_root()
    
    # Run the resource setup script
    resource_script = os.path.join(project_root, 'src', 'frontend', 'setup_resources.py')
    
    if os.path.exists(resource_script):
        try:
            # Make setup_resources.py executable
            os.chmod(resource_script, 0o755)
        except Exception:
            # On Windows this might fail, but it's not a problem
            pass
        
        # Run the script
        return run_command(f"{sys.executable} {resource_script}")
    else:
        print(f"Error: Resource setup script not found at {resource_script}")
        return False

def create_launcher():
    """Create a platform-specific launcher."""
    print_section("Creating Game Launcher")
    
    # Get project root
    project_root = get_project_root()
    
    if platform.system() == "Windows":
        # Create a Windows .bat launcher
        launcher_path = os.path.join(project_root, 'play_gomoku.bat')
        with open(launcher_path, 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting Five in a Row (Gomoku)...\n')
            f.write(f'"{sys.executable}" "{os.path.join(project_root, "play_gomoku.py")}"\n')
        
        print(f"Created Windows launcher: {launcher_path}")
    else:
        # Create a shell script launcher
        launcher_path = os.path.join(project_root, 'play_gomoku.sh')
        with open(launcher_path, 'w') as f:
            f.write('#!/bin/bash\n\n')
            f.write('echo "Starting Five in a Row (Gomoku)..."\n')
            f.write(f'"{sys.executable}" "{os.path.join(project_root, "play_gomoku.py")}"\n')
        
        # Make it executable
        try:
            os.chmod(launcher_path, 0o755)
        except Exception as e:
            print(f"Warning: Could not make launcher executable: {e}")
        
        print(f"Created Unix launcher: {launcher_path}")
    
    return True

def create_desktop_shortcut():
    """Create a desktop shortcut for easier access."""
    print_section("Creating Desktop Shortcut")
    
    # Get project root
    project_root = get_project_root()
    
    try:
        # Get user's desktop path
        if platform.system() == "Windows":
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # On Linux, it might be in a different language
            if not os.path.exists(desktop):
                # Try common desktop locations
                possible_desktops = [
                    os.path.join(os.path.expanduser("~"), "Desktop"),
                    os.path.join(os.path.expanduser("~"), "Escritorio"),
                    os.path.join(os.path.expanduser("~"), "Bureau"),
                    os.path.join(os.path.expanduser("~"), "Schreibtisch")
                ]
                
                for path in possible_desktops:
                    if os.path.exists(path):
                        desktop = path
                        break
        
        if platform.system() == "Windows":
            # Create a Windows shortcut
            shortcut_path = os.path.join(desktop, "Five in a Row.lnk")
            
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.TargetPath = os.path.join(project_root, "play_gomoku.bat")
                shortcut.WorkingDirectory = project_root
                shortcut.IconLocation = os.path.join(project_root, "resources", "gomoku_icon.ico")
                shortcut.save()
                print(f"Created desktop shortcut: {shortcut_path}")
            except ImportError:
                print("Warning: win32com.client module not available, skipping Windows shortcut creation")
                return False
                
        elif platform.system() == "Darwin":  # macOS
            # Create a macOS .command file
            shortcut_path = os.path.join(desktop, "Five in a Row.command")
            
            with open(shortcut_path, 'w') as f:
                f.write('#!/bin/bash\n\n')
                f.write(f'cd "{project_root}"\n')
                f.write('./play_gomoku.sh\n')
            
            # Make it executable
            os.chmod(shortcut_path, 0o755)
            
            # Try to set a custom icon for the macOS shortcut
            icon_path = os.path.join(project_root, 'resources', 'gomoku_icon.png')
            if os.path.exists(icon_path):
                try:
                    # Use AppleScript to set the icon (this requires user with admin privileges)
                    icon_script = f'''
                    tell application "Finder"
                        set file_path to POSIX file "{shortcut_path}" as alias
                        set icon_path to POSIX file "{icon_path}" as alias
                        set icon of file_path to icon of icon_path
                    end tell
                    '''
                    subprocess.run(['osascript', '-e', icon_script], capture_output=True, check=False)
                    print("Set custom icon for macOS shortcut")
                except Exception as e:
                    print(f"Note: Could not set custom icon for shortcut: {e}")
                    
            print(f"Created macOS desktop shortcut: {shortcut_path}")
            
        elif platform.system() == "Linux":
            # Create a Linux .desktop file
            shortcut_path = os.path.join(desktop, "five-in-a-row.desktop")
            
            with open(shortcut_path, 'w') as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Name=Five in a Row\n")
                f.write("Comment=Play the classic Gomoku game\n")
                f.write(f"Exec={os.path.join(project_root, 'play_gomoku.sh')}\n")
                f.write(f"Icon={os.path.join(project_root, 'resources', 'gomoku_icon.png')}\n")
                f.write("Terminal=false\n")
                f.write("Categories=Game;BoardGame;\n")
            
            # Make it executable
            os.chmod(shortcut_path, 0o755)
            print(f"Created Linux desktop shortcut: {shortcut_path}")
            
        return True
    except Exception as e:
        print(f"Warning: Could not create desktop shortcut: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Five in a Row (Gomoku) Installer')
    parser.add_argument('--no-build', action='store_true', help='Skip building the C++ backend')
    parser.add_argument('--no-deps', action='store_true', help='Skip Python package installation')
    parser.add_argument('--no-shortcut', action='store_true', help='Skip desktop shortcut creation')
    
    args = parser.parse_args()
    
    print_section("Five in a Row (Gomoku) Installer")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    success = True
    
    # Build the backend if not skipped
    if not args.no_build:
        success = success and build_backend()
    
    # Set up Python environment if not skipped
    if not args.no_deps:
        success = success and setup_python_environment()
    
    # Set up resources
    success = success and setup_resources()
    
    # Create launcher
    success = success and create_launcher()
    
    # Create desktop shortcut if not skipped
    if not args.no_shortcut:
        create_desktop_shortcut()  # Optional, don't affect success status
    
    if success:
        print_section("Installation Completed Successfully")
        print("You can now start the game by running:")
        
        if platform.system() == "Windows":
            print("  play_gomoku.bat")
        else:
            print("  ./play_gomoku.sh")
            
        print("\nOr by double-clicking the desktop shortcut.")
    else:
        print_section("Installation Completed with Errors")
        print("Please check the output above for details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
