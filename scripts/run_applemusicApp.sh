#!/bin/bash

# Detect the operating system and set the correct Python and Pip commands
OS="$(uname)"
case $OS in
    'Linux'|'Darwin')
        echo "Running on $OS"
        PYTHON_EXECUTABLE=$(which python3)
        PIP_EXECUTABLE=$(which pip3)
        ;;
    'CYGWIN'*|'MINGW'*|'MSYS'*|'MINGW32'*|'MINGW64'*)
        echo "Running on Windows"
        PYTHON_EXECUTABLE=python
        PIP_EXECUTABLE=pip
        ;;
    *)
        echo "Unknown OS: $OS"
        exit 1
        ;;
esac

# Check if Python and Pip executables are found
if [ -z "$PYTHON_EXECUTABLE" ]; then
    echo "Python executable not found. Exiting..."
    exit 1
fi

if [ -z "$PIP_EXECUTABLE" ]; then
    echo "Pip executable not found. Exiting..."
    exit 1
fi

echo "Using Python: $PYTHON_EXECUTABLE"
echo "Using Pip: $PIP_EXECUTABLE"

# Install the required Python packages
$PIP_EXECUTABLE install --upgrade pip
$PIP_EXECUTABLE install -r ../requirements.txt

# Navigate to the src directory
cd src/artistScrapers

# Run the Python script to scrape artist names (assuming this script exists and is needed)
$PYTHON_EXECUTABLE mysteryland2024_scraper.py

# Navigate to the Apple Music scripts directory
cd ../appleMusicApp

# Run the Apple Music API scripts in the required order
$PYTHON_EXECUTABLE get_artist_ids.py
$PYTHON_EXECUTABLE get_top_tracks.py
$PYTHON_EXECUTABLE make_playlist.py

echo "All Apple Music scripts have been executed successfully!"