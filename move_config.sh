#!/bin/bash

# Define the source and destination paths
SOURCE="/boot/config_echo.txt"
DESTINATION="$(pwd)/config.py"

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