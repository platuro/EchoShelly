#!/bin/bash

# Define the source and destination paths
SOURCE="/boot/config_echo.txt"
DESTINATION="$(pwd)/config.py"

# Perform a git fetch to check for changes
git fetch

# Check if there are any local changes
if ! git diff-index --quiet HEAD --; then
    # Perform a hard reset to discard local changes
    git reset --hard
    echo "Local changes detected and discarded."
fi

# Perform a git pull to ensure the repository is up-to-date
git pull

# Check if main.py is already running
if pgrep -f "python3 $(pwd)/main.py" > /dev/null
then
    echo "main.py is already running. Aborting script execution."
    exit 1
fi

# Check if the source file exists
if [ -f "$SOURCE" ]; then
    # Move the file from /boot to the current directory
    cp "$SOURCE" "$DESTINATION"
    echo "Moved $SOURCE to $DESTINATION"
else
    echo "File $SOURCE does not exist."
fi

# Run the main.py script
python3 "$(pwd)/main.py"
