#!/usr/bin/env python3
import os
import datetime
import shutil

# Get the base directory (project root)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get project name from the base directory
project_name = os.path.basename(base_dir)

# Generate timestamp in a file-friendly format
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# Define source and target files
source_file = os.path.join(base_dir, "repomix-output.txt")
target_file = os.path.join(base_dir, f"CodeBase_{project_name}-{timestamp}.txt")

# Check if source file exists
if os.path.exists(source_file):
    # Copy the file (original remains intact)
    shutil.copy2(source_file, target_file)
    print(f"File copied successfully: {target_file}")
else:
    print(f"Error: Source file {source_file} not found")
