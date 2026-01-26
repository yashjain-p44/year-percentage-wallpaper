#!/bin/bash
# Double-clickable script to generate and set wallpaper
# Place this file on your Desktop for easy access

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the Python script
python3 generate_and_set_wallpaper.py

# Keep terminal open if double-clicked (wait for user input)
if [ -t 0 ]; then
    # Running in terminal, don't wait
    :
else
    # Double-clicked, wait for user to see output
    echo ""
    echo "Press any key to close..."
    read -n 1
fi
