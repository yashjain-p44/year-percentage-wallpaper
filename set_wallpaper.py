#!/usr/bin/env python3
"""
Script to set a PNG image as the Mac wallpaper for the current space.
Usage: python set_wallpaper.py <path_to_image.png>
"""

import sys
import os
import subprocess


def set_wallpaper(image_path):
    """
    Set the given image as the Mac wallpaper for the current space using AppleScript.
    
    Args:
        image_path (str): Path to the image file
    """
    # Convert to absolute path
    abs_path = os.path.abspath(image_path)
    
    # Verify file exists
    if not os.path.exists(abs_path):
        print(f"Error: File not found: {abs_path}")
        sys.exit(1)
    
    # Verify it's a file (not a directory)
    if not os.path.isfile(abs_path):
        print(f"Error: Path is not a file: {abs_path}")
        sys.exit(1)
    
    # Escape quotes in path for AppleScript
    escaped_path = abs_path.replace('"', '\\"')
    
    # AppleScript command to set wallpaper for current desktop
    applescript = f'''
    tell application "System Events"
        tell current desktop
            set picture to "{escaped_path}"
        end tell
    end tell
    '''
    
    try:
        # Execute AppleScript
        subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Wallpaper set successfully: {abs_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting wallpaper: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python set_wallpaper.py <path_to_image.png>")
        print("Example: python set_wallpaper.py ~/Pictures/my_wallpaper.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    set_wallpaper(image_path)


if __name__ == "__main__":
    main()
