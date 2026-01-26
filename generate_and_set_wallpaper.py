#!/usr/bin/env python3
"""
Combined script that generates a new wallpaper and sets it as the current space wallpaper.
Double-click this script or run from terminal.
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import subprocess
import sys

# ---- CONFIG ----
WIDTH, HEIGHT = 2560, 1600  # MacBook Pro resolution (adjust if needed)
BACKGROUND_COLOR = "black"
TEXT_COLOR = "white"
FONT_SIZE = 300
OUTPUT_DIR = os.path.expanduser("~/wallpapers")
FONT_PATH = "/System/Library/Fonts/SFNS.ttf"  # System font
# ----------------


def set_wallpaper(image_path):
    """
    Set the given image as the Mac wallpaper for the current space using AppleScript.
    
    Args:
        image_path (str): Path to the image file
    """
    abs_path = os.path.abspath(image_path)
    
    # Escape quotes in path for AppleScript
    escaped_path = abs_path.replace('"', '\\"')
    
    # AppleScript command to set wallpaper
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
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting wallpaper: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error setting wallpaper: {e}")
        return False


def generate_wallpaper():
    """Generate a new wallpaper image with the year progress percentage."""
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Calculate percentage of year completed
    now = datetime.now()
    year_start = datetime(now.year, 1, 1, 0, 0, 0, 0)
    year_end = datetime(now.year + 1, 1, 1, 0, 0, 0, 0)
    
    total_seconds_in_year = (year_end - year_start).total_seconds()
    elapsed_seconds = (now - year_start).total_seconds()
    
    percentage = (elapsed_seconds / total_seconds_in_year) * 100
    text = f"{percentage:.8f}"
    
    # Generate filename with timestamp
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"dynamic_wallpaper_{timestamp}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    # Create image
    img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception:
        # Fallback to default font if system font not available
        font = ImageFont.load_default()
    
    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (WIDTH - text_width) / 2
    y = (HEIGHT - text_height) / 2
    
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)
    
    # Save the new image
    img.save(output_path)
    print(f"✓ Wallpaper image generated: {output_path}")
    
    return output_path


def main():
    """Main function to generate and set wallpaper."""
    print("Generating new wallpaper...")
    
    try:
        # Generate the wallpaper
        wallpaper_path = generate_wallpaper()
        
        # Set it as wallpaper
        print("Setting wallpaper...")
        if set_wallpaper(wallpaper_path):
            print(f"✓ Wallpaper set successfully!")
            print(f"  Image: {wallpaper_path}")
        else:
            print("✗ Failed to set wallpaper, but image was generated.")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
