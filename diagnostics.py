#!/usr/bin/env python3
"""
Diagnostics tool for Five in a Row (Gomoku) game.
This script helps diagnose and fix common issues with the game installation.
"""

import os
import sys
import platform
import subprocess
import shutil
import ctypes
from pathlib import Path

def check_python_version():
    """Check if the Python version is compatible."""
    print("Checking Python version...")
    python_version = platform.python_version()
    print(f"  Python version: {python_version}")
    
    major, minor, _ = [int(n) for n in python_version.split('.')]
    if major < 3 or (major == 3 and minor < 6):
        print("  [WARNING] Python 3.6 or higher is recommended")
        return False
    else:
        print("  [OK] Python version is supported")
        return True

def check_required_packages():
    """Check if all required Python packages are installed."""
    print("Checking required Python packages...")
    required_packages = ['PyQt5', 'pillow', 'scipy']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  [OK] {package} is installed")
        except ImportError:
            print(f"  [MISSING] {package} is not installed")
            missing.append(package)
    
    if missing:
        print("\nSome required packages are missing. Install them with:")
        print(f"  {sys.executable} -m pip install {' '.join(missing)}")
        return False
    return True

def check_library():
    """Check if the C++ library is properly built and accessible."""
    print("Checking C++ backend library...")
    
    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Define the library filename based on the platform
    if platform.system() == "Windows":
        lib_name = "gomoku.dll"
    elif platform.system() == "Darwin":  # macOS
        lib_name = "libgomoku.dylib"
    else:  # Linux
        lib_name = "libgomoku.so"
    
    # Check in standard locations
    locations = [
        os.path.join(project_root, "lib", lib_name),
        os.path.join(project_root, "build", lib_name),
    ]
    
    # Add platform-specific locations
    if platform.system() == "Windows":
        locations.append(os.path.join(project_root, "build", "Release", lib_name))
    
    found_lib = None
    for loc in locations:
        if os.path.exists(loc):
            found_lib = loc
            print(f"  [OK] Library found at: {loc}")
            break
    
    if not found_lib:
        print(f"  [MISSING] Library not found in any standard location")
        print("\nThe C++ backend library is missing. You need to build it:")
        if platform.system() == "Windows":
            print("  build.bat")
        else:
            print("  ./build.sh")
        return False
    
    # Try to load the library
    try:
        print(f"  Attempting to load library from: {found_lib}")
        lib = ctypes.CDLL(found_lib)
        print(f"  [OK] Successfully loaded the library")
        
        # Check if the library has the expected functions
        required_functions = [
            'create_engine',
            'destroy_engine',
            'make_move',
            'get_best_move',
            'reset_game'
        ]
        
        missing_functions = []
        for func in required_functions:
            if not hasattr(lib, func):
                missing_functions.append(func)
        
        if missing_functions:
            print(f"  [WARNING] Library is missing required functions: {', '.join(missing_functions)}")
            return False
        else:
            print(f"  [OK] Library has all required functions")
            return True
    except Exception as e:
        print(f"  [ERROR] Failed to load the library: {e}")
        return False

def check_resources():
    """Check if all required resources are available."""
    print("Checking resources...")
    
    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Define required resources
    required_resources = [
        'gomoku_icon.png'
    ]
    
    # Check multiple possible resource locations
    resource_locations = [
        os.path.join(project_root, 'resources'),
        os.path.join(project_root, 'src', 'resources')
    ]
    
    resource_status = {}
    for resource in required_resources:
        resource_status[resource] = None
        
        for location in resource_locations:
            path = os.path.join(location, resource)
            if os.path.exists(path):
                resource_status[resource] = path
                break
    
    # Print status
    all_found = True
    for resource, path in resource_status.items():
        if path:
            print(f"  [OK] {resource} found at: {path}")
        else:
            print(f"  [MISSING] {resource} not found")
            all_found = False
    
    if not all_found:
        print("\nSome resources are missing. Run the setup script to generate them:")
        print(f"  {sys.executable} src/frontend/setup_resources.py")
        return False
    
    return True

def check_file_permissions():
    """Check if script files have the correct permissions."""
    print("Checking file permissions...")
    
    # Only relevant on Unix-like systems
    if platform.system() == "Windows":
        print("  [SKIPPED] Permissions check not applicable on Windows")
        return True
    
    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Files that need to be executable
    executable_files = [
        os.path.join(project_root, "build.sh"),
        os.path.join(project_root, "play_gomoku.sh"),
        os.path.join(project_root, "play_gomoku.py"),
        os.path.join(project_root, "src", "frontend", "setup_resources.py"),
        os.path.join(project_root, "src", "frontend", "gomoku_app.py"),
        os.path.join(project_root, "src", "frontend", "create_icon.py"),
    ]
    
    all_ok = True
    for file_path in executable_files:
        if os.path.exists(file_path):
            if os.access(file_path, os.X_OK):
                print(f"  [OK] {os.path.basename(file_path)} is executable")
            else:
                print(f"  [WARNING] {os.path.basename(file_path)} is not executable")
                all_ok = False
        else:
            print(f"  [MISSING] {os.path.basename(file_path)} does not exist")
    
    if not all_ok:
        print("\nSome script files are not executable. Fix this with:")
        print("  chmod +x build.sh play_gomoku.sh play_gomoku.py src/frontend/*.py")
        return False
    
    return True

def fix_permissions():
    """Fix permissions on script files."""
    print("Fixing file permissions...")
    
    if platform.system() == "Windows":
        print("  [SKIPPED] Permission fixing not applicable on Windows")
        return
    
    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Files that need to be executable
    executable_files = [
        os.path.join(project_root, "build.sh"),
        os.path.join(project_root, "play_gomoku.sh"),
        os.path.join(project_root, "play_gomoku.py"),
        os.path.join(project_root, "src", "frontend", "setup_resources.py"),
        os.path.join(project_root, "src", "frontend", "gomoku_app.py"),
        os.path.join(project_root, "src", "frontend", "create_icon.py"),
    ]
    
    for file_path in executable_files:
        if os.path.exists(file_path):
            try:
                os.chmod(file_path, 0o755)  # rwxr-xr-x
                print(f"  [FIXED] Made {os.path.basename(file_path)} executable")
            except Exception as e:
                print(f"  [ERROR] Could not fix permissions on {os.path.basename(file_path)}: {e}")

def rebuild_library():
    """Rebuild the C++ library."""
    print("Rebuilding C++ library...")
    
    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Make sure build and lib directories exist
    os.makedirs(os.path.join(project_root, "build"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "lib"), exist_ok=True)
    
    # Run the appropriate build script
    if platform.system() == "Windows":
        bat_file = os.path.join(project_root, "build.bat")
        if os.path.exists(bat_file):
            print("  Running build.bat...")
            try:
                subprocess.run(["cmd", "/c", bat_file], check=True)
                print("  [OK] Build completed successfully")
            except subprocess.CalledProcessError as e:
                print(f"  [ERROR] Build failed: {e}")
        else:
            print("  [ERROR] build.bat not found")
    else:
        sh_file = os.path.join(project_root, "build.sh")
        if os.path.exists(sh_file):
            print("  Running build.sh...")
            try:
                # Make sure the script is executable
                os.chmod(sh_file, 0o755)
                subprocess.run([sh_file], check=True)
                print("  [OK] Build completed successfully")
            except subprocess.CalledProcessError as e:
                print(f"  [ERROR] Build failed: {e}")
        else:
            print("  [ERROR] build.sh not found")

def regenerate_resources():
    """Regenerate all game resources."""
    print("Regenerating game resources...")
    
    # Get project root and resource script path
    project_root = os.path.dirname(os.path.abspath(__file__))
    setup_script = os.path.join(project_root, "src", "frontend", "setup_resources.py")
    
    if os.path.exists(setup_script):
        print("  Running setup_resources.py...")
        try:
            # Make sure the script is executable
            if platform.system() != "Windows":
                os.chmod(setup_script, 0o755)
            
            subprocess.run([sys.executable, setup_script], check=True)
            print("  [OK] Resources generated successfully")
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Resource generation failed: {e}")
    else:
        print("  [ERROR] setup_resources.py not found")

def run_full_test():
    """Run a full diagnostic test and fix issues if requested."""
    print("=" * 60)
    print("Five in a Row (Gomoku) - Diagnostic Tool")
    print("=" * 60)
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("=" * 60)
    
    # Run all checks
    python_ok = check_python_version()
    packages_ok = check_required_packages()
    library_ok = check_library()
    resources_ok = check_resources()
    permissions_ok = check_file_permissions()
    
    # Summarize issues
    print("\n" + "=" * 60)
    print("Diagnostic Summary")
    print("=" * 60)
    
    issues = []
    if not python_ok:
        issues.append("Python version below recommended (3.6+)")
    if not packages_ok:
        issues.append("Missing required Python packages")
    if not library_ok:
        issues.append("C++ library issues")
    if not resources_ok:
        issues.append("Missing game resources")
    if not permissions_ok:
        issues.append("Incorrect file permissions")
    
    if not issues:
        print("No issues detected! The game should work correctly.")
    else:
        print("The following issues were detected:")
        for i, issue in enumerate(issues):
            print(f"  {i+1}. {issue}")
        
        # Ask user if they want to fix the issues
        fix_it = input("\nWould you like to attempt to fix these issues? (y/n): ").lower().strip()
        
        if fix_it == 'y':
            print("\n" + "=" * 60)
            print("Fixing Issues")
            print("=" * 60)
            
            if not packages_ok:
                print("\nInstalling missing Python packages...")
                for package in ['PyQt5', 'pillow', 'scipy']:
                    try:
                        __import__(package)
                    except ImportError:
                        print(f"  Installing {package}...")
                        subprocess.run([sys.executable, "-m", "pip", "install", package], check=False)
            
            if not permissions_ok:
                print("\nFixing file permissions...")
                fix_permissions()
            
            if not library_ok:
                print("\nRebuilding C++ library...")
                rebuild_library()
            
            if not resources_ok:
                print("\nRegenerating game resources...")
                regenerate_resources()
            
            print("\nAll fixes applied. Please run this diagnostic tool again to verify.")
        else:
            print("\nNo changes made. Please fix the issues manually.")

if __name__ == "__main__":
    run_full_test()
