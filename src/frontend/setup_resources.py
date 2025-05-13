#!/usr/bin/env python3
"""
Resource Management Script for Five in a Row (Gomoku) game.
This script helps consolidate resources from various locations into a single directory.
"""

import os
import shutil
import sys
import subprocess

def find_project_root():
    """Find the project root directory based on the current script's location."""
    # Start from script's location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for markers that indicate we're in the project root
    while current_dir and not os.path.exists(os.path.join(current_dir, 'src')) and not os.path.exists(os.path.join(current_dir, 'build.sh')):
        parent = os.path.dirname(current_dir)
        if parent == current_dir:  # We've reached the filesystem root
            return None
        current_dir = parent
    
    return current_dir

def consolidate_resources():
    """Gather resources from various locations and copy them to the main resources directory."""
    # Find the project root
    project_root = find_project_root()
    if not project_root:
        print("Error: Could not determine project root directory.")
        return False
    
    print(f"Project root: {project_root}")
    
    # Define the main resources directory (we'll use this as the primary location)
    main_resources_dir = os.path.join(project_root, 'resources')
    
    # Make sure the main resources directory exists
    if not os.path.exists(main_resources_dir):
        os.makedirs(main_resources_dir)
        print(f"Created main resources directory: {main_resources_dir}")
    
    # List of locations where resources might be
    resource_locations = [
        os.path.join(project_root, 'src', 'resources'),
        os.path.join(project_root, 'Projects', 'School', 'five-in-a-row', 'resources'),
    ]
    
    # Add additional platform-specific resource locations
    if sys.platform.startswith('darwin'):  # macOS
        # macOS might store resources in different locations
        resource_locations.extend([
            os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'five-in-a-row', 'resources'),
            '/Applications/five-in-a-row.app/Contents/Resources'
        ])
    elif sys.platform.startswith('win'):  # Windows
        # Windows might store resources in AppData or Program Files
        resource_locations.extend([
            os.path.join(os.getenv('APPDATA', ''), 'five-in-a-row', 'resources'),
            os.path.join(os.getenv('PROGRAMFILES', ''), 'five-in-a-row', 'resources')
        ])
    elif sys.platform.startswith('linux'):  # Linux
        # Linux might store resources in standard XDG directories
        resource_locations.extend([
            os.path.join(os.path.expanduser('~'), '.local', 'share', 'five-in-a-row', 'resources'),
            '/usr/share/five-in-a-row/resources',
            '/usr/local/share/five-in-a-row/resources'
        ])
    
    # Resource files we're looking for
    resource_files = [
        'gomoku_icon.png',
        'settings.json'
    ]
    
    # Keep track of which resources we've found and copied
    found_resources = set()
    
    # First, check if resources already exist in main directory
    for filename in resource_files:
        if os.path.exists(os.path.join(main_resources_dir, filename)):
            found_resources.add(filename)
            print(f"Resource already exists in main directory: {filename}")
    
    # Look for missing resources in other locations
    for location in resource_locations:
        if not os.path.exists(location):
            continue
        
        print(f"Checking location: {location}")
        for filename in resource_files:
            if filename in found_resources:
                continue  # Skip files we've already found
                
            source_path = os.path.join(location, filename)
            if os.path.exists(source_path):
                dest_path = os.path.join(main_resources_dir, filename)
                if not os.path.exists(dest_path):
                    try:
                        # Try to create symbolic link first
                        try:
                            if sys.platform == "win32":
                                # On Windows, need admin privileges or developer mode enabled
                                import subprocess
                                subprocess.call(['mklink', dest_path, source_path], shell=True)
                            else:
                                # On Unix systems
                                os.symlink(source_path, dest_path)
                            print(f"Created symbolic link from {source_path} to {dest_path}")
                        except (OSError, subprocess.SubprocessError):
                            # Fall back to copying if symlink fails
                            shutil.copyfile(source_path, dest_path)
                            print(f"Copied {filename} from {location} to {main_resources_dir}")
                    except Exception as e:
                        print(f"Error creating link or copying file {filename}: {e}")
                found_resources.add(filename)
    
    # Generate missing resources if needed
    missing_resources = set(resource_files) - found_resources
    if missing_resources:
        print(f"Missing resources that need to be generated: {missing_resources}")
        
        # For icon file, run create_icon.py
        if 'gomoku_icon.png' in missing_resources:
            create_icon_path = os.path.join(project_root, 'src', 'frontend', 'create_icon.py')
            if os.path.exists(create_icon_path):
                print("Running create_icon.py to generate the game icon...")
                try:
                    # Change to project root for proper paths
                    os.chdir(project_root)
                    
                    # Run the script
                    os.system(f"python3 {create_icon_path}")
                except Exception as e:
                    print(f"Error generating icon: {e}")
    
    # Check if all resources are now available
    missing_after = []
    for filename in resource_files:
        if not os.path.exists(os.path.join(main_resources_dir, filename)):
            if not filename == 'settings.json':  # Settings file might not exist yet
                missing_after.append(filename)
    
    if missing_after:
        print(f"Warning: Still missing resources: {missing_after}")
        return False
    else:
        print("All resources successfully consolidated!")
        return True

if __name__ == "__main__":
    consolidate_resources()
