#!/bin/bash
# File: UpdateGitHub.sh
# Path: OllamaModelEditor/scripts/UpdateGitHub.sh
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Updates existing GitHub repository with new project structure

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

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo -e "${RED}Error: Not in a git repository.${NC}"
    echo -e "Please run this script from within your OllamaModelEditor git repository."
    exit 1
fi

PrintHeader "Updating GitHub Repository"

# Define repository details
GITHUB_USERNAME="CallMeChewy"
PROJECT_NAME="OllamaModelEditor"
EXPECTED_REPO_URL="https://github.com/$GITHUB_USERNAME/$PROJECT_NAME.git"

# Verify repository
echo -e "${YELLOW}Current repository:${NC}"
ACTUAL_REPO_URL=$(git config --get remote.origin.url)
echo -e "Expected repository: ${GREEN}$GITHUB_USERNAME/$PROJECT_NAME${NC}"
echo -e "Expected URL: ${GREEN}$EXPECTED_REPO_URL${NC}"
echo -e "\nActual repository URL: ${BLUE}$ACTUAL_REPO_URL${NC}"
echo -e "\nRemote details:"
git remote -v

# Check if this is the expected repository
if [[ "$ACTUAL_REPO_URL" == "$EXPECTED_REPO_URL" || "$ACTUAL_REPO_URL" == "git@github.com:$GITHUB_USERNAME/$PROJECT_NAME.git" ]]; then
    echo -e "\n${GREEN}✓ This is the correct repository.${NC}"
else
    echo -e "\n${YELLOW}⚠️ Warning: The current repository does not match the expected repository.${NC}"
fi

echo -e "\n${YELLOW}Is this the correct repository you want to update? (y/n)${NC}"
read answer
if [ "$answer" != "${answer#[Yy]}" ]; then
    # Proceed with update
    PrintHeader "Backing up any existing changes"
    
    # Check if there are uncommitted changes
    if ! git diff --quiet HEAD; then
        # Create backup branch with timestamp
        BACKUP_BRANCH="backup_$(date +%Y%m%d_%H%M%S)"
        echo -e "Creating backup branch: ${BACKUP_BRANCH}"
        git checkout -b $BACKUP_BRANCH
        git add .
        git commit -m "Backup before repository update"
        echo -e "${GREEN}Backup created on branch: ${BACKUP_BRANCH}${NC}"
        
        # Switch back to main branch
        git checkout main || git checkout master
    else
        echo -e "No uncommitted changes to backup."
    fi
    
    PrintHeader "Preparing for update"
    
    # Ask if user wants to keep any specific files
    echo -e "${YELLOW}Do you want to keep any specific files from the current repository? (y/n)${NC}"
    read keep_files
    if [ "$keep_files" != "${keep_files#[Yy]}" ]; then
        echo -e "Please enter file/directory patterns to keep, separated by spaces:"
        echo -e "(For example: README.md LICENSE .github/workflows)"
        read -a files_to_keep
        
        # Create a temporary directory to store files
        TEMP_DIR=$(mktemp -d)
        echo -e "Temporarily storing files in: ${TEMP_DIR}"
        
        # Copy files to keep to temp directory
        for file in "${files_to_keep[@]}"; do
            if [ -e "$file" ]; then
                # Create directory structure in temp
                mkdir -p "$TEMP_DIR/$(dirname "$file")"
                cp -r "$file" "$TEMP_DIR/$(dirname "$file")/"
                echo -e "Saved: $file"
            else
                echo -e "${YELLOW}Warning: $file not found${NC}"
            fi
        done
    fi
    
    PrintHeader "Removing existing files"
    
    # Get root directory of the git repository
    REPO_ROOT=$(git rev-parse --show-toplevel)
    
    # Remove all files except .git directory and temporary script
    find "$REPO_ROOT" -mindepth 1 -not -path "$REPO_ROOT/.git*" -not -path "$0" | xargs rm -rf
    
    echo -e "${GREEN}Repository cleaned successfully.${NC}"
    
    # Restore kept files if any
    if [ "$keep_files" != "${keep_files#[Yy]}" ] && [ -d "$TEMP_DIR" ]; then
        echo -e "Restoring files you chose to keep..."
        cp -r "$TEMP_DIR"/* "$REPO_ROOT"/ 2>/dev/null || true
        rm -rf "$TEMP_DIR"
    fi
    
    PrintHeader "Adding new project files"
    
    # Assuming we're in the OllamaModelEditor directory
    echo -e "Copying new files to repository..."
    
    # Get the current directory
    CURRENT_DIR=$(pwd)
    
    # Copy all project files to the repository root
    rsync -av --exclude='.git/' --exclude='scripts/UpdateGitHub.sh' "$CURRENT_DIR"/* "$REPO_ROOT"/
    
    echo -e "${GREEN}New files copied successfully.${NC}"
    
    PrintHeader "Committing changes"
    
    # Add all new files
    git add .
    
    # Commit changes
    git commit -m "Complete project restructure to AIDEV-PascalCase standards"
    
    echo -e "${GREEN}Changes committed successfully.${NC}"
    
    PrintHeader "Push to GitHub"
    
    echo -e "${YELLOW}Do you want to push these changes to GitHub now? (y/n)${NC}"
    read push_now
    if [ "$push_now" != "${push_now#[Yy]}" ]; then
        # Determine default branch name
        DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
        
        echo -e "Pushing to ${DEFAULT_BRANCH} branch..."
        git push origin $DEFAULT_BRANCH
        
        echo -e "${GREEN}Changes pushed to GitHub successfully.${NC}"
    else
        echo -e "${BLUE}Changes were not pushed. You can push manually with:${NC}"
        echo -e "  git push origin main  # or 'master' depending on your default branch"
    fi
    
    PrintHeader "Update Complete"
    echo -e "${GREEN}Your GitHub repository has been updated successfully!${NC}"
    
else
    echo -e "${RED}Operation cancelled.${NC}"
    exit 1
fi
