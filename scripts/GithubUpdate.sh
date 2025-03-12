#!/bin/bash

# GitHub Update Script for OllamaModelEditor
# This script automates the process of committing and pushing changes to GitHub

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GitHub Update Script for OllamaModelEditor${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed.${NC}"
    exit 1
fi

# Check if the current directory is a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: This directory is not a git repository.${NC}"
    echo -e "${YELLOW}Run 'git init' to initialize a new repository.${NC}"
    exit 1
fi

# Check if remote origin exists
if ! git remote get-url origin &> /dev/null; then
    echo -e "${RED}Error: Remote 'origin' not configured.${NC}"
    echo -e "${YELLOW}Use 'git remote add origin <url>' to add a remote repository.${NC}"
    exit 1
fi

# Function to get commit message
get_commit_message() {
    # Default commit message
    default_message="Update OllamaModelEditor files"
    
    # If a message was provided as an argument, use it
    if [ -n "$1" ]; then
        echo "$1"
    else
        # Ask for commit message with default
        read -p "Enter commit message [$default_message]: " message
        echo "${message:-$default_message}"
    fi
}

# Check git status
echo -e "${BLUE}Checking repository status...${NC}"
git status

# Store current status output
status_output=$(git status --porcelain)

# If there are no changes, exit
if [ -z "$status_output" ]; then
    echo -e "${GREEN}No changes to commit. Repository is up to date.${NC}"
    exit 0
fi

# Show summary of changes
echo -e "${YELLOW}Changes detected:${NC}"
echo -e "${YELLOW}-------------------${NC}"
modified_files=$(echo "$status_output" | grep '^ M\|^M ' | wc -l)
untracked_files=$(echo "$status_output" | grep '^??' | wc -l)
deleted_files=$(echo "$status_output" | grep '^ D\|^D ' | wc -l)

echo -e "${YELLOW}Modified files: ${NC}$modified_files"
echo -e "${YELLOW}New files: ${NC}$untracked_files"
echo -e "${YELLOW}Deleted files: ${NC}$deleted_files"
echo -e "${YELLOW}-------------------${NC}"

# Prompt to continue
read -p "Continue with update? (y/n): " continue_update
if [[ ! "$continue_update" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Update canceled.${NC}"
    exit 0
fi

# Stage all changes
echo -e "${BLUE}Staging all changes...${NC}"
git add .

# Show what's staged
echo -e "${BLUE}Files staged for commit:${NC}"
git status

# Get commit message (from argument or prompt)
commit_message=$(get_commit_message "$1")

# Commit changes
echo -e "${BLUE}Committing changes...${NC}"
git commit -m "$commit_message"

# Check if commit was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Commit failed. Exiting.${NC}"
    exit 1
fi

# Prompt before pushing
read -p "Push changes to GitHub? (y/n): " push_changes
if [[ ! "$push_changes" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Changes committed but not pushed.${NC}"
    echo -e "${YELLOW}Run 'git push origin main' to push changes when ready.${NC}"
    exit 0
fi

# Push changes
echo -e "${BLUE}Pushing changes to GitHub...${NC}"
git push origin main

# Check if push was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Success! All changes have been pushed to GitHub.${NC}"
else
    echo -e "${RED}Push failed. You may need to pull changes first with 'git pull origin main'.${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}GitHub update complete!${NC}"
echo -e "${BLUE}========================================${NC}"
