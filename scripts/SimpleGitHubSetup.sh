#!/bin/bash
# File: SimpleGitHubSetup.sh
# Path: OllamaModelEditor/scripts/SimpleGitHubSetup.sh
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Simple script to reset and initialize GitHub repository

# Text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print section headers
PrintHeader() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is required but not installed.${NC}"
    echo -e "Please install git and try again."
    exit 1
fi

PrintHeader "GitHub Repository Setup"

# GitHub username and repository name
GITHUB_USERNAME="CallMeChewy"
REPO_NAME="OllamaModelEditor"

echo -e "This script will set up your GitHub repository for:"
echo -e "  ${GREEN}$GITHUB_USERNAME/$REPO_NAME${NC}"
echo -e "\n${YELLOW}Is this correct? (y/n)${NC}"
read answer

if [ "$answer" != "${answer#[Yy]}" ]; then
    # Make sure we're in the project root directory (where Main.py is)
    if [ ! -f "Main.py" ]; then
        echo -e "${RED}Error: Main.py not found. Please run this script from the project root directory.${NC}"
        exit 1
    fi

    PrintHeader "Initializing Git Repository"
    
    # Remove any existing git directory
    echo -e "Removing any existing Git data..."
    rm -rf .git
    
    # Initialize new git repository
    echo -e "Initializing new Git repository..."
    git init
    
    # Create .gitignore file
    echo -e "Creating .gitignore file..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Project specific
*.log
.env

# Custom exclusions
..Exclude/
..Scripts/
..Next/
..Vision/
EOF
    
    # Add all files
    echo -e "Adding files to Git..."
    git add .
    
    # Make initial commit
    echo -e "Creating initial commit..."
    git commit -m "Initial commit of OllamaModelEditor project"
    
    PrintHeader "Connecting to GitHub"
    
    # Add GitHub as remote origin
    echo -e "Adding GitHub remote..."
    git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git
    
    echo -e "${YELLOW}Do you want to push to GitHub now? (y/n)${NC}"
    echo -e "${YELLOW}Note: This will overwrite any existing content in your GitHub repository.${NC}"
    read push_now
    
    if [ "$push_now" != "${push_now#[Yy]}" ]; then
        PrintHeader "Pushing to GitHub"
        
        echo -e "Enter your GitHub username: $GITHUB_USERNAME"
        
        # Force push to overwrite any existing content
        echo -e "Pushing to GitHub (you'll be prompted for your password or access token)..."
        git push -f origin master
        
        # Check if push was successful
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Successfully pushed to GitHub!${NC}"
            echo -e "Your repository is now available at: ${BLUE}https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
        else
            echo -e "${RED}Push failed.${NC}"
            echo -e "You may need to:"
            echo -e "1. Create a personal access token on GitHub:"
            echo -e "   ${BLUE}https://github.com/settings/tokens${NC}"
            echo -e "2. Use that token as your password when prompted"
            echo -e "\nOr push manually with:"
            echo -e "  git push -f origin master"
        fi
    else
        echo -e "${BLUE}Skipping push to GitHub. You can push later with:${NC}"
        echo -e "  git push -f origin master"
    fi
    
    PrintHeader "Setup Complete"
    echo -e "${GREEN}Your repository has been set up successfully!${NC}"
    
else
    echo -e "${RED}Operation cancelled.${NC}"
    exit 1
fi
