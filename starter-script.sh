#!/bin/bash
# Starter script for Ollama Model Editor
# This script helps with first-time setup and running the application

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}Ollama Model Editor Starter${RESET}\n"

# Check if Python is installed
echo -e "${YELLOW}Checking Python installation...${RESET}"
if command -v python3 &>/dev/null; then
    PYTHON=python3
    echo -e "${GREEN}✓ Python 3 found${RESET}"
else
    if command -v python &>/dev/null; then
        PYTHON=python
        PYTHON_VERSION=$(python --version 2>&1)
        if [[ $PYTHON_VERSION != *"Python 3"* ]]; then
            echo -e "${RED}✗ Python 3 not found. Please install Python 3.8 or higher.${RESET}"
            exit 1
        fi
        echo -e "${GREEN}✓ Python 3 found as 'python'${RESET}"
    else
        echo -e "${RED}✗ Python not found. Please install Python 3.8 or higher.${RESET}"
        exit 1
    fi
fi

# Check for virtual environment
echo -e "${YELLOW}Checking for virtual environment...${RESET}"
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓ Virtual environment found${RESET}"
else
    echo -e "${YELLOW}Creating virtual environment...${RESET}"
    $PYTHON -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to create virtual environment. Please install venv package.${RESET}"
        exit 1
    fi
    echo -e "${GREEN}✓ Virtual environment created${RESET}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${RESET}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Unix/Linux/MacOS
    source .venv/bin/activate
fi
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to activate virtual environment.${RESET}"
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment activated${RESET}"

# Install requirements
echo -e "${YELLOW}Checking dependencies...${RESET}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to install requirements.${RESET}"
        exit 1
    fi
    echo -e "${GREEN}✓ Dependencies installed${RESET}"
else
    echo -e "${YELLOW}Installing minimal dependencies...${RESET}"
    pip install pyyaml
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to install minimal dependencies.${RESET}"
        exit 1
    fi
    echo -e "${GREEN}✓ Minimal dependencies installed${RESET}"
fi

# Check if Ollama is running
echo -e "${YELLOW}Checking Ollama service...${RESET}"
if ! command -v ollama &>/dev/null; then
    echo -e "${RED}✗ Ollama not found in PATH. Please install Ollama first.${RESET}"
    echo -e "   Visit https://ollama.ai/download for installation instructions."
    echo -e "   After installing, restart this script.${RESET}"
    exit 1
fi

# Use a simple 'list' command to check if Ollama is running
ollama list &>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Ollama service is not running.${RESET}"
    echo -e "${YELLOW}Attempting to start Ollama service...${RESET}"
    
    # Try to start Ollama (this varies by platform)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open -a Ollama
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - try systemd if available
        if command -v systemctl &>/dev/null; then
            sudo systemctl start ollama
        else
            # Fallback to manual start
            echo -e "${YELLOW}Please start Ollama manually and try again.${RESET}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Please start Ollama manually and try again.${RESET}"
        exit 1
    fi
    
    # Check if start was successful
    echo -e "${YELLOW}Waiting for Ollama service to start...${RESET}"
    sleep 5
    ollama list &>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to start Ollama service. Please start it manually.${RESET}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Ollama service is running${RESET}"

# Count available models
MODEL_COUNT=$(ollama list | grep -v "NAME" | grep -v "^$" | wc -l)
MODEL_COUNT=$(echo $MODEL_COUNT | tr -d '[:space:]')
if [ "$MODEL_COUNT" -eq "0" ]; then
    echo -e "${YELLOW}⚠ No Ollama models found. You may want to pull a model first.${RESET}"
    echo -e "   Example: ${BOLD}ollama pull llama3${RESET}"
else
    echo -e "${GREEN}✓ Found $MODEL_COUNT Ollama models${RESET}"
fi

# Check for required code files
echo -e "${YELLOW}Checking for required code files...${RESET}"
MISSING_FILES=0
for FILE in "Main.py" "Core/ConfigManager.py" "Core/ModelManager.py" "Core/ParameterHandler.py" "UI/MainWindow.py"; do
    if [ ! -f "$FILE" ]; then
        echo -e "${RED}✗ Missing required file: $FILE${RESET}"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo -e "${RED}✗ Missing $MISSING_FILES required files. Please ensure all project files are present.${RESET}"
    exit 1
fi
echo -e "${GREEN}✓ All required code files are present${RESET}"

# Everything is ready, start the application
echo -e "\n${GREEN}${BOLD}All checks passed! Starting Ollama Model Editor...${RESET}\n"
$PYTHON Main.py

# Deactivate virtual environment on exit
deactivate
