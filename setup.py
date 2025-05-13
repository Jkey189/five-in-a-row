#!/usr/bin/env python3
"""
Cross-platform One-Click Installer for Five in a Row (Gomoku)
This script performs a complete installation and setup of the game on any platform.
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
import time
import urllib.request
from pathlib import Path

# ANSI color codes for prettier output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD} {text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_step(text):
    """Print a step message."""
    print(f"{Colors.BLUE}→ {text}{Colors.ENDC}")

def run_command(command, cwd=None, show_output=True):
    """Run a shell command and return the result."""
    print_step(f"Running: {command}")
    
    try:
        # Use shell=True for complex commands (pipes, redirections)
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE if show_output else subprocess.DEVNULL,
            stderr=subprocess.PIPE if show_output else subprocess.DEVNULL,
            universal_newlines=True,
            check=False  # Don't raise exception on non-zero return code
        )
        
        if show_output and result.stdout:
            print(result.stdout.strip())
            
        if result.returncode != 0 and show_output:
            print_warning(f"Command exited with code {result.returncode}")
            if result.stderr:
                print_warning("Error output:")
                print(result.stderr.strip())
            
        return result.returncode == 0
    except Exception as e:
        print_error(f"Failed to execute command: {e}")
        return False

def get_project_root():
    """Get the absolute path to the project root directory."""
    return os.path.dirname(os.path.abspath(__file__))

def check_prerequisites():
    """Check if all required tools are installed."""
    print_header("Checking Prerequisites")
    
    all_ok = True
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Python version: {python_version}")
    
    major, minor, _ = [int(n) for n in python_version.split('.')]
    if major < 3 or (major == 3 and minor < 6):
        print_warning("Python 3.6 or higher is recommended")
        all_ok = False
    else:
        print_success("Python version is supported")
    
    # Check for CMake
    try:
        result = subprocess.run(
            ["cmake", "--version"],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        if result.returncode == 0:
            cmake_version = result.stdout.split('\n')[0]
            print_success(f"CMake found: {cmake_version}")
        else:
            print_warning("CMake not found. Please install CMake.")
            all_ok = False
    except:
        print_warning("CMake not found. Please install CMake.")
        all_ok = False
    
    # Check for C++ compiler
    if platform.system() == "Windows":
        try:
            # Check for Visual C++
            result = subprocess.run(
                ["cl", "/?"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if result.returncode == 0:
                print_success("Visual C++ compiler found")
            else:
                # Check for MinGW G++
                result = subprocess.run(
                    ["g++", "--version"],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                if result.returncode == 0:
                    print_success(f"G++ compiler found: {result.stdout.split('\\n')[0]}")
                else:
                    print_warning("No C++ compiler found. Please install Visual Studio or MinGW.")
                    all_ok = False
        except:
            print_warning("No C++ compiler found. Please install Visual Studio or MinGW.")
            all_ok = False
    else:
        # Check for GCC/Clang on Unix systems
        try:
            result = subprocess.run(
                ["c++", "--version"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if result.returncode == 0:
                print_success(f"C++ compiler found: {result.stdout.split('\\n')[0]}")
            else:
                print_warning("No C++ compiler found. Please install GCC or Clang.")
                all_ok = False
        except:
            print_warning("No C++ compiler found. Please install GCC or Clang.")
            all_ok = False
    
    return all_ok

def install_python_packages():
    """Install required Python packages."""
    print_header("Installing Python Packages")
    
    packages = ["PyQt5", "pillow", "scipy"]
    all_ok = True
    
    for package in packages:
        print_step(f"Installing {package}...")
        if run_command(f"{sys.executable} -m pip install {package}", show_output=True):
            print_success(f"{package} installed/updated successfully")
        else:
            print_warning(f"Failed to install {package}")
            all_ok = False
    
    return all_ok

def build_backend():
    """Build the C++ backend library."""
    print_header("Building C++ Backend")
    
    project_root = get_project_root()
    
    # Create build and lib directories if they don't exist
    build_dir = os.path.join(project_root, "build")
    lib_dir = os.path.join(project_root, "lib")
    
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(lib_dir, exist_ok=True)
    
    # Build based on platform
    if platform.system() == "Windows":
        # Try running the batch file first
        batch_file = os.path.join(project_root, "build.bat")
        if os.path.exists(batch_file):
            print_step("Running build.bat...")
            if run_command(batch_file, cwd=project_root):
                print_success("Build completed successfully")
                return True
            else:
                print_warning("build.bat failed, trying CMake directly...")
        
        # If batch file doesn't exist or fails, use CMake directly
        print_step("Building with CMake...")
        
        # Configure
        if run_command("cmake ..", cwd=build_dir):
            # Build
            if run_command("cmake --build . --config Release", cwd=build_dir):
                # Copy DLL to lib directory
                if os.path.exists(os.path.join(build_dir, "Release", "gomoku.dll")):
                    shutil.copy(
                        os.path.join(build_dir, "Release", "gomoku.dll"),
                        os.path.join(lib_dir, "gomoku.dll")
                    )
                    print_success("Copied gomoku.dll to lib directory")
                    return True
                elif os.path.exists(os.path.join(build_dir, "gomoku.dll")):
                    shutil.copy(
                        os.path.join(build_dir, "gomoku.dll"),
                        os.path.join(lib_dir, "gomoku.dll")
                    )
                    print_success("Copied gomoku.dll to lib directory")
                    return True
                else:
                    print_error("Built library not found")
                    return False
            else:
                print_error("Build failed")
                return False
        else:
            print_error("CMake configuration failed")
            return False
    else:
        # Unix-like platforms (macOS, Linux)
        build_script = os.path.join(project_root, "build.sh")
        
        # Make build script executable
        try:
            os.chmod(build_script, 0o755)
        except Exception as e:
            print_warning(f"Could not make build script executable: {e}")
        
        # Run build script
        if run_command(build_script, cwd=project_root):
            print_success("Build completed successfully")
            return True
        else:
            print_warning("build.sh failed, trying CMake directly...")
            
            # If shell script fails, use CMake directly
            if run_command("cmake ..", cwd=build_dir):
                if run_command("make", cwd=build_dir):
                    # Copy shared library to lib directory
                    lib_name = None
                    if platform.system() == "Darwin":  # macOS
                        lib_name = "libgomoku.dylib"
                    else:  # Linux
                        lib_name = "libgomoku.so"
                        
                    if os.path.exists(os.path.join(build_dir, lib_name)):
                        shutil.copy(
                            os.path.join(build_dir, lib_name),
                            os.path.join(lib_dir, lib_name)
                        )
                        print_success(f"Copied {lib_name} to lib directory")
                        return True
                    else:
                        print_error("Built library not found")
                        return False
                else:
                    print_error("Build failed")
                    return False
            else:
                print_error("CMake configuration failed")
                return False

def setup_resources():
    """Set up game resources."""
    print_header("Setting Up Game Resources")
    
    project_root = get_project_root()
    
    # Create resources directory if it doesn't exist
    resources_dir = os.path.join(project_root, "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # Try running the setup_resources.py script
    resource_script = os.path.join(project_root, "src", "frontend", "setup_resources.py")
    
    if os.path.exists(resource_script):
        try:
            # Make script executable on Unix-like platforms
            if platform.system() != "Windows":
                os.chmod(resource_script, 0o755)
        except Exception:
            pass
        
        if run_command(f"{sys.executable} {resource_script}"):
            print_success("Resource setup completed successfully")
            return True
        else:
            print_warning("Resource setup script failed")
    else:
        print_warning("Resource setup script not found")
    
    # If script failed or not found, try manual resource setup
    print_step("Attempting manual resource setup...")
    
    # Check if resources already exist
    required_resources = [
        "gomoku_icon.png"
    ]
    
    missing = []
    for resource in required_resources:
        if not os.path.exists(os.path.join(resources_dir, resource)):
            missing.append(resource)
    
    if not missing:
        print_success("All required resources already exist")
        return True
    
    # Try to generate missing resources
    print_step("Generating missing resources...")
    
    # Sound files are no longer needed
    
    if "gomoku_icon.png" in missing:
        icon_script = os.path.join(project_root, "src", "frontend", "create_icon.py")
        if os.path.exists(icon_script):
            if run_command(f"{sys.executable} {icon_script}"):
                print_success("Game icon generated successfully")
            else:
                print_warning("Failed to generate game icon")
                return False
    
    # Check if resources are now available
    still_missing = []
    for resource in required_resources:
        if not os.path.exists(os.path.join(resources_dir, resource)):
            still_missing.append(resource)
    
    if still_missing:
        print_warning(f"Some resources could not be generated: {', '.join(still_missing)}")
        return False
    else:
        print_success("All resources are now available")
        return True

def create_launchers():
    """Create platform-specific launchers."""
    print_header("Creating Game Launchers")
    
    project_root = get_project_root()
    
    # Create the main Python launcher script (play_gomoku.py)
    launcher_py_path = os.path.join(project_root, "play_gomoku.py")
    
    # Check if the launcher script already exists
    if not os.path.exists(launcher_py_path):
        print_step("Creating Python launcher script...")
        
        launcher_code = """#!/usr/bin/env python3
\"\"\"
Launcher script for Five in a Row (Gomoku) game.
This script ensures proper paths are set before launching the game.
\"\"\"

import os
import sys
import platform
import subprocess
import shutil

def run_game():
    \"\"\"Set up environment and launch the game.\"\"\"
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
        
        # For Windows, also check Release directory
        if platform.system() == 'Windows' and not os.path.exists(build_lib_path):
            release_path = os.path.join(project_root, 'build', 'Release', library_filename)
            if os.path.exists(release_path):
                build_lib_path = release_path
        
        # Check if library exists in build directory
        if os.path.exists(build_lib_path):
            # Copy to lib directory
            shutil.copyfile(build_lib_path, lib_path)
            print(f"Copied library from {build_lib_path} to {lib_path}")
        else:
            print(f"Warning: Library not found at {build_lib_path}")
    
    # Run resource setup script
    resource_setup_script = os.path.join(project_root, 'src', 'frontend', 'setup_resources.py')
    if os.path.exists(resource_setup_script):
        print("\\n=== Setting up resources ===")
        subprocess.call([sys.executable, resource_setup_script])
    
    # Launch the game
    game_script = os.path.join(project_root, 'src', 'frontend', 'gomoku_app.py')
    if os.path.exists(game_script):
        print("\\n=== Launching the game ===")
        os.environ['PYTHONPATH'] = project_root  # Add project root to Python path
        result = subprocess.call([sys.executable, game_script])
        return result
    else:
        print(f"Error: Game script not found at {game_script}")
        return 1

if __name__ == "__main__":
    sys.exit(run_game())
"""
        
        with open(launcher_py_path, "w") as f:
            f.write(launcher_code)
        
        # Make it executable on Unix-like platforms
        if platform.system() != "Windows":
            os.chmod(launcher_py_path, 0o755)
        
        print_success("Created Python launcher script")
    else:
        print_success("Python launcher script already exists")
    
    # Create platform-specific launchers
    if platform.system() == "Windows":
        # Create Windows batch file
        bat_path = os.path.join(project_root, "play_gomoku.bat")
        
        if not os.path.exists(bat_path):
            print_step("Creating Windows batch file...")
            
            with open(bat_path, "w") as f:
                f.write("@echo off\n")
                f.write("echo Starting Five in a Row (Gomoku)...\n")
                f.write("echo.\n\n")
                f.write("REM Make sure we're in the right directory\n")
                f.write("cd /d \"%~dp0\"\n\n")
                f.write("REM Set up Python path environment variable\n")
                f.write("set PYTHONPATH=%CD%\n\n")
                f.write("REM Check if Python is available\n")
                f.write("python --version >nul 2>&1\n")
                f.write("if %ERRORLEVEL% neq 0 (\n")
                f.write("    echo Python not found in PATH. Please make sure Python is installed.\n")
                f.write("    echo Press any key to exit...\n")
                f.write("    pause > nul\n")
                f.write("    exit /b 1\n")
                f.write(")\n\n")
                f.write("REM Run the launcher script\n")
                f.write("python play_gomoku.py\n\n")
                f.write("REM If the game exited with an error, wait for user input\n")
                f.write("if %ERRORLEVEL% neq 0 (\n")
                f.write("    echo.\n")
                f.write("    echo The game exited with an error. Check the output above for details.\n")
                f.write("    echo Press any key to exit...\n")
                f.write("    pause > nul\n")
                f.write(")\n")
            
            print_success("Created Windows batch file")
        else:
            print_success("Windows batch file already exists")
    else:
        # Create shell script for Unix-like platforms
        sh_path = os.path.join(project_root, "play_gomoku.sh")
        
        if not os.path.exists(sh_path):
            print_step("Creating shell script...")
            
            with open(sh_path, "w") as f:
                f.write("#!/bin/bash\n\n")
                f.write("echo \"Starting Five in a Row (Gomoku)...\"\n")
                f.write("echo \"\"\n\n")
                f.write("# Get the directory where the script is located\n")
                f.write("SCRIPT_DIR=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" && pwd )\"\n\n")
                f.write("# Change to the script directory\n")
                f.write("cd \"$SCRIPT_DIR\"\n\n")
                f.write("# Set up Python path environment variable\n")
                f.write("export PYTHONPATH=\"$SCRIPT_DIR\"\n\n")
                f.write("# Check if Python is available\n")
                f.write("if ! command -v python3 &> /dev/null; then\n")
                f.write("    echo \"Python 3 not found. Please make sure Python 3 is installed.\"\n")
                f.write("    echo \"Press Enter to exit...\"\n")
                f.write("    read\n")
                f.write("    exit 1\n")
                f.write("fi\n\n")
                f.write("# Run the launcher script\n")
                f.write("python3 play_gomoku.py\n\n")
                f.write("# If the game exited with an error, wait for user input\n")
                f.write("if [ $? -ne 0 ]; then\n")
                f.write("    echo \"\"\n")
                f.write("    echo \"The game exited with an error. Check the output above for details.\"\n")
                f.write("    echo \"Press Enter to exit...\"\n")
                f.write("    read\n")
                f.write("fi\n")
            
            # Make it executable
            os.chmod(sh_path, 0o755)
            
            print_success("Created shell script")
        else:
            print_success("Shell script already exists")
            
            # Make sure it's executable
            try:
                os.chmod(sh_path, 0o755)
            except:
                pass
    
    return True

def create_desktop_shortcut():
    """Create a desktop shortcut for the game."""
    print_header("Creating Desktop Shortcut")
    
    # Get user's desktop path
    home = os.path.expanduser("~")
    desktop = os.path.join(home, "Desktop")
    
    # Check if desktop directory exists (could have different name in non-English locales)
    if not os.path.isdir(desktop):
        desktop_candidates = [
            os.path.join(home, "Desktop"),
            os.path.join(home, "Escritorio"),
            os.path.join(home, "Bureau"),
            os.path.join(home, "Schreibtisch"),
            os.path.join(home, "桌面"),
            os.path.join(home, "デスクトップ")
        ]
        
        for candidate in desktop_candidates:
            if os.path.isdir(candidate):
                desktop = candidate
                break
        else:
            print_warning("Could not locate desktop directory")
            return False
    
    project_root = get_project_root()
    
    if platform.system() == "Windows":
        # Try to create a Windows shortcut (.lnk file)
        try:
            shortcut_path = os.path.join(desktop, "Five in a Row.lnk")
            
            try:
                # Use the pywin32 module if available
                import win32com.client
                
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.TargetPath = os.path.join(project_root, "play_gomoku.bat")
                shortcut.WorkingDirectory = project_root
                
                # Add icon if available
                icon_path = os.path.join(project_root, "resources", "gomoku_icon.png")
                if os.path.exists(icon_path):
                    shortcut.IconLocation = icon_path
                
                shortcut.Save()
                
                print_success(f"Created desktop shortcut at: {shortcut_path}")
                return True
            except ImportError:
                # If pywin32 is not available, try with PowerShell
                print_step("pywin32 module not available, trying PowerShell...")
                
                ps_command = f"""
                $WshShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
                $Shortcut.TargetPath = "{os.path.join(project_root, 'play_gomoku.bat').replace('\\', '\\\\')}"
                $Shortcut.WorkingDirectory = "{project_root.replace('\\', '\\\\')}"
                $Shortcut.Save()
                """
                
                with open(os.path.join(project_root, "create_shortcut.ps1"), "w") as f:
                    f.write(ps_command)
                
                if run_command("powershell -ExecutionPolicy Bypass -File create_shortcut.ps1", cwd=project_root):
                    # Remove the temporary script
                    os.unlink(os.path.join(project_root, "create_shortcut.ps1"))
                    
                    print_success(f"Created desktop shortcut at: {shortcut_path}")
                    return True
                else:
                    print_warning("Failed to create shortcut with PowerShell")
                    
                    # Try with a simple copy of the batch file as last resort
                    shutil.copy(
                        os.path.join(project_root, "play_gomoku.bat"),
                        os.path.join(desktop, "Five in a Row.bat")
                    )
                    
                    print_success("Created a batch file on desktop as a shortcut")
                    return True
        except Exception as e:
            print_warning(f"Failed to create Windows shortcut: {e}")
            return False
    elif platform.system() == "Darwin":  # macOS
        try:
            # Create a macOS .command file
            command_path = os.path.join(desktop, "Five in a Row.command")
            
            with open(command_path, "w") as f:
                f.write("#!/bin/bash\n\n")
                f.write(f"cd \"{project_root}\"\n")
                f.write("./play_gomoku.sh\n")
            
            # Make it executable
            os.chmod(command_path, 0o755)
            
            # Try to set a custom icon using AppleScript
            icon_path = os.path.join(project_root, "resources", "gomoku_icon.png")
            if os.path.exists(icon_path):
                # Convert PNG to ICNS if needed (simplified)
                try:
                    import Cocoa
                    import Quartz
                    import os
                    
                    # Read PNG image
                    image_data = Cocoa.NSData.dataWithContentsOfFile_(icon_path)
                    if image_data:
                        image = Quartz.CIImage.imageWithData_(image_data)
                        if image:
                            icon_path = os.path.join(project_root, "resources", "gomoku_icon.icns")
                            image.writeToURL_options_colorSpace_(
                                Cocoa.NSURL.fileURLWithPath_(icon_path),
                                0,
                                Quartz.CGColorSpaceCreateDeviceRGB()
                            )
                except ImportError:
                    # Can't convert to ICNS, but can still try to set icon with AppleScript
                    pass
                
                # Try to set icon with AppleScript
                applescript = f'''
                tell application "Finder"
                    set file_path to POSIX file "{command_path}" as alias
                    set icon_path to POSIX file "{icon_path}" as alias
                    set icon of file_path to icon of icon_path
                end tell
                '''
                
                try:
                    subprocess.run(["osascript", "-e", applescript], capture_output=True)
                except:
                    pass
            
            print_success(f"Created desktop shortcut at: {command_path}")
            return True
        except Exception as e:
            print_warning(f"Failed to create macOS shortcut: {e}")
            return False
    else:  # Linux
        try:
            # Create a Linux .desktop file
            desktop_path = os.path.join(desktop, "five-in-a-row.desktop")
            
            with open(desktop_path, "w") as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Name=Five in a Row\n")
                f.write("Comment=Play the classic Gomoku game\n")
                f.write(f"Exec={os.path.join(project_root, 'play_gomoku.sh')}\n")
                f.write(f"Icon={os.path.join(project_root, 'resources', 'gomoku_icon.png')}\n")
                f.write("Terminal=false\n")
                f.write("Categories=Game;BoardGame;\n")
            
            # Make it executable
            os.chmod(desktop_path, 0o755)
            
            print_success(f"Created desktop shortcut at: {desktop_path}")
            return True
        except Exception as e:
            print_warning(f"Failed to create Linux shortcut: {e}")
            return False

def run_cleanup():
    """Clean up temporary files."""
    print_header("Cleaning Up")
    
    project_root = get_project_root()
    
    # List of patterns to clean up
    cleanup_patterns = [
        "*.o", "*.obj", "*.pyc", 
        "__pycache__", "*.log"
    ]
    
    for pattern in cleanup_patterns:
        if platform.system() == "Windows":
            run_command(f"del /s /q {pattern}", cwd=project_root, show_output=False)
        else:
            run_command(f"find . -name '{pattern}' -delete", cwd=project_root, show_output=False)
    
    print_success("Cleanup completed")
    return True

def main():
    """Main installer function."""
    parser = argparse.ArgumentParser(description="Five in a Row (Gomoku) Installer")
    parser.add_argument("--no-deps", action="store_true", help="Skip installing Python dependencies")
    parser.add_argument("--no-build", action="store_true", help="Skip building C++ backend")
    parser.add_argument("--no-shortcut", action="store_true", help="Skip creating desktop shortcut")
    parser.add_argument("--no-cleanup", action="store_true", help="Skip cleanup step")
    
    args = parser.parse_args()
    
    print_header("Five in a Row (Gomoku) Installer")
    
    # Print system information
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Project root: {get_project_root()}")
    print("\nStarting installation...")
    
    # Check prerequisites
    prerequisites_ok = check_prerequisites()
    if not prerequisites_ok:
        print_warning("Some prerequisites are missing, but we'll try to continue anyway")
    
    # Install Python packages if not skipped
    if not args.no_deps:
        deps_ok = install_python_packages()
        if not deps_ok:
            print_warning("Some Python packages could not be installed")
    else:
        print_step("Skipping Python dependencies installation")
    
    # Build backend if not skipped
    if not args.no_build:
        build_ok = build_backend()
        if not build_ok:
            print_error("Failed to build C++ backend")
            print("Please check the error messages above and make sure you have a C++ compiler and CMake installed.")
            return 1
    else:
        print_step("Skipping C++ backend building")
    
    # Set up resources
    resources_ok = setup_resources()
    if not resources_ok:
        print_warning("Some resources could not be set up")
    
    # Create launchers
    launchers_ok = create_launchers()
    if not launchers_ok:
        print_warning("Failed to create launchers")
    
    # Create desktop shortcut if not skipped
    if not args.no_shortcut:
        shortcut_ok = create_desktop_shortcut()
        if not shortcut_ok:
            print_warning("Failed to create desktop shortcut")
    else:
        print_step("Skipping desktop shortcut creation")
    
    # Run cleanup if not skipped
    if not args.no_cleanup:
        run_cleanup()
    
    print_header("Installation Complete")
    
    print("You can now run the game with:")
    if platform.system() == "Windows":
        print(f"  {Colors.BOLD}play_gomoku.bat{Colors.ENDC}")
    else:
        print(f"  {Colors.BOLD}./play_gomoku.sh{Colors.ENDC}")
    
    print("\nOr directly with Python:")
    print(f"  {Colors.BOLD}python play_gomoku.py{Colors.ENDC}")
    
    print("\nEnjoy your game!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
