#!/bin/bash

# Get the project directory name (basename of current directory)
PROJECT_NAME=$(basename "$(pwd)")

# Generate timestamp in a file-friendly format
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Define source and target files
SOURCE_FILE="repomix-output.txt"
TARGET_FILE="CodeBase_${PROJECT_NAME}-${TIMESTAMP}.txt"

# Check if source file exists
if [ -f "$SOURCE_FILE" ]; then
    # Copy the file (original remains intact)
    cp "$SOURCE_FILE" "$TARGET_FILE"
    echo "File copied successfully: $TARGET_FILE"
else
    echo "Error: Source file $SOURCE_FILE not found"
fi
