#!/usr/bin/env python3
"""
Generates a year-progress wallpaper for every connected display and sets it.
Double-click this script or run from terminal.

Run with --help to see the available options.
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import argparse
import glob
import json
import os
import subprocess
import sys

# ---- CONFIG ----
DEFAULT_SIZE = (2560, 1600)  # Used only if displays cannot be detected
BACKGROUND_COLOR = "black"
TEXT_COLOR = "white"
FONT_SIZE_RATIO = 0.1875  # Font size as a fraction of image height (300px at 1600px tall)
OUTPUT_DIR = os.path.expanduser("~/wallpapers")
FONT_PATH = "/System/Library/Fonts/SFNS.ttf"  # System font
DEFAULT_DECIMALS = 8
DEFAULT_KEEP = 5  # Number of generated wallpapers per run to keep on disk
FILE_PREFIX = "dynamic_wallpaper_"
# ----------------

DETECT_SCREENS_JXA = """
ObjC.import('AppKit');
JSON.stringify($.NSScreen.screens.js.map(function (s) {
    var f = s.frame, k = s.backingScaleFactor;
    return [Math.round(f.size.width * k), Math.round(f.size.height * k)];
}));
"""


def detect_screen_sizes():
    """
    Return the pixel resolution of each connected display, in system order.
    Falls back to DEFAULT_SIZE if detection fails.
    """
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", DETECT_SCREENS_JXA],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        sizes = [tuple(s) for s in json.loads(result.stdout.strip())]
        if sizes:
            return sizes
    except Exception as e:
        print(f"Could not detect displays ({e}); using {DEFAULT_SIZE[0]}x{DEFAULT_SIZE[1]}")
    return [DEFAULT_SIZE]


def year_progress_text(now, decimals):
    """Return the percentage of the year elapsed, formatted as a string."""
    year_start = datetime(now.year, 1, 1)
    year_end = datetime(now.year + 1, 1, 1)
    percentage = (now - year_start).total_seconds() / (year_end - year_start).total_seconds() * 100
    return f"{percentage:.{decimals}f}"


def render_wallpaper(text, size, output_path):
    """Render the given text centered on a background of the given size."""
    width, height = size
    img = Image.new("RGB", size, BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    font_size = int(height * FONT_SIZE_RATIO)
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except Exception:
        # Fallback to default font if system font not available
        font = ImageFont.load_default()

    # Shrink the font if the text would overflow the display width
    # (e.g. portrait displays or many decimals).
    bbox = draw.textbbox((0, 0), text, font=font)
    max_width = width * 0.9
    if bbox[2] - bbox[0] > max_width and hasattr(font, "size"):
        font = ImageFont.truetype(FONT_PATH, max(1, int(font.size * max_width / (bbox[2] - bbox[0]))))
        bbox = draw.textbbox((0, 0), text, font=font)

    # Center using the bbox offsets so the text is visually centered
    x = (width - (bbox[2] - bbox[0])) / 2 - bbox[0]
    y = (height - (bbox[3] - bbox[1])) / 2 - bbox[1]
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)

    img.save(output_path)


def generate_wallpapers(decimals):
    """Generate one wallpaper per display. Returns the list of image paths in display order."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    now = datetime.now()
    text = year_progress_text(now, decimals)
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    paths = []
    by_size = {}  # Reuse one image for displays with identical resolution
    for index, size in enumerate(detect_screen_sizes()):
        if size not in by_size:
            filename = f"{FILE_PREFIX}{timestamp}_{size[0]}x{size[1]}.png"
            output_path = os.path.join(OUTPUT_DIR, filename)
            render_wallpaper(text, size, output_path)
            print(f"✓ Wallpaper image generated for display {index + 1}: {output_path}")
            by_size[size] = output_path
        paths.append(by_size[size])
    return paths


def cleanup_old_wallpapers(keep, protect=()):
    """
    Delete older generated wallpapers, keeping the newest `keep` files.
    Only touches files matching this script's own naming pattern, and never
    deletes anything in `protect` (the images that were just set).
    """
    files = sorted(
        glob.glob(os.path.join(OUTPUT_DIR, f"{FILE_PREFIX}*.png")),
        key=os.path.getmtime,
        reverse=True,
    )
    protected = {os.path.abspath(p) for p in protect}
    for old in files[keep:]:
        if os.path.abspath(old) in protected:
            continue
        try:
            os.remove(old)
        except OSError as e:
            print(f"Could not remove {old}: {e}")


def set_wallpapers(image_paths):
    """
    Set wallpapers via AppleScript: image_paths[i] goes on desktop i+1.
    Note: this assumes System Events lists desktops in the same order as the
    displays reported by detect_screen_sizes().
    """
    lines = []
    for i, path in enumerate(image_paths, start=1):
        escaped = os.path.abspath(path).replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'        try\n            set picture of desktop {i} to "{escaped}"\n        end try')
    applescript = 'tell application "System Events"\n' + "\n".join(lines) + "\nend tell"

    try:
        subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting wallpaper: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error setting wallpaper: {e}")
        return False


def parse_args():
    parser = argparse.ArgumentParser(description="Generate and set a year-progress wallpaper.")
    parser.add_argument(
        "--decimals", type=int, default=DEFAULT_DECIMALS,
        help=f"Decimal places to show (default: {DEFAULT_DECIMALS}). Use fewer for slower update intervals.",
    )
    parser.add_argument(
        "--keep", type=int, default=DEFAULT_KEEP,
        help=f"Number of generated wallpaper files to keep on disk (default: {DEFAULT_KEEP}).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    keep = max(args.keep, 1)
    print("Generating new wallpaper...")

    try:
        wallpaper_paths = generate_wallpapers(args.decimals)

        print("Setting wallpaper...")
        ok = set_wallpapers(wallpaper_paths)
        cleanup_old_wallpapers(keep, protect=wallpaper_paths)

        if ok:
            print(f"✓ Wallpaper set successfully on {len(wallpaper_paths)} display(s)!")
        else:
            print("✗ Failed to set wallpaper, but image was generated.")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
