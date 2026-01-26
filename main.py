from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import os

# ---- CONFIG ----
WIDTH, HEIGHT = 2560, 1600  # MacBook Pro resolution (adjust if needed)
BACKGROUND_COLOR = "black"
TEXT_COLOR = "white"
FONT_SIZE = 300
OUTPUT_DIR = os.path.expanduser("~/wallpapers")
FONT_PATH = "/System/Library/Fonts/SFNS.ttf"  # System font
# ----------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Your logic here - Calculate percentage of year completed
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
OUTPUT_PATH = os.path.join(OUTPUT_DIR, filename)

# Create image
img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

# Center text
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

x = (WIDTH - text_width) / 2
y = (HEIGHT - text_height) / 2

draw.text((x, y), text, fill=TEXT_COLOR, font=font)

# Save the new image
img.save(OUTPUT_PATH)
print(f"Wallpaper image saved to: {OUTPUT_PATH}")
