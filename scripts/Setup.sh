#!/bin/bash
# File: Setup.sh
# Path: OllamaModelEditor/scripts/Setup.sh
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Setup script for OllamaModelEditor project

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

# Function to check command existence
CheckCommand() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is required but not installed.${NC}"
        echo -e "Please install $1 and try again."
        exit 1
    fi
}

# Function to create directories from project structure
CreateDirectories() {
    PrintHeader "Creating Project Structure"
    
    # Main directories
    mkdir -p OllamaModelEditor
    cd OllamaModelEditor
    
    # Create directory structure
    mkdir -p .github/workflows
    mkdir -p .github/ISSUE_TEMPLATE
    mkdir -p Core
    mkdir -p GUI/Assets/{icons,themes,fonts}
    mkdir -p GUI/Components
    mkdir -p GUI/Dialogs
    mkdir -p GUI/Windows
    mkdir -p Tests/{UnitTests,IntegrationTests,UITests}
    mkdir -p Utils
    mkdir -p Features
    mkdir -p docs/screenshots
    mkdir -p scripts
    
    echo -e "${GREEN}Directory structure created successfully.${NC}"
}

# Function to set up virtual environment
SetupVirtualEnv() {
    PrintHeader "Setting Up Python Virtual Environment"
    
    # Create virtual environment
    python3 -m venv .venv
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Create initial requirements.txt
    cat > requirements.txt << EOF
PySide6>=6.5.0
pytest>=7.3.1
pytest-qt>=4.2.0
requests>=2.28.2
pyyaml>=6.0
loguru>=0.7.0
EOF
    
    # Install requirements
    pip install -r requirements.txt
    
    echo -e "${GREEN}Virtual environment created and dependencies installed.${NC}"
}

# Function to initialize Git repository
SetupGit() {
    PrintHeader "Setting Up Git Repository"
    
    # Initialize git repository
    git init
    
    # Create .gitignore
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
EOF
    
    # Create GitHub workflow for CI
    mkdir -p .github/workflows
    cat > .github/workflows/ci.yml << EOF
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest
EOF
    
    # Create PR template
    cat > .github/PULL_REQUEST_TEMPLATE.md << EOF
## Description
<!-- Provide a brief description of the changes in this PR -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Other (please describe):

## Testing Performed
<!-- Describe the testing done to verify your changes -->

## Checklist
- [ ] My code follows the AIDEV-PascalCase standards of this project
- [ ] I have performed a self-review of my own code
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have updated the documentation accordingly
EOF
    
    # Create issue templates
    cat > .github/ISSUE_TEMPLATE/bug_report.md << EOF
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows, macOS, Linux]
 - Python Version: [e.g. 3.8, 3.9]
 - Application Version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
EOF
    
    cat > .github/ISSUE_TEMPLATE/feature_request.md << EOF
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
EOF
    
    # Initial commit
    git add .
    git commit -m "Initial project structure"
    
    echo -e "${GREEN}Git repository initialized successfully.${NC}"
}

# Function to set up GitHub remote (if credentials available)
SetupGitHubRemote() {
    PrintHeader "Setting Up GitHub Remote"
    
    echo -e "${YELLOW}Would you like to set up the GitHub remote now? (y/n)${NC}"
    read answer
    
    if [ "$answer" != "${answer#[Yy]}" ]; then
        echo -e "Enter your GitHub username (default: CallMeChewy):"
        read username
        username=${username:-CallMeChewy}
        
        echo -e "Enter the repository name (default: OllamaModelEditor):"
        read repo
        repo=${repo:-OllamaModelEditor}
        
        echo -e "Setting up remote repository..."
        git remote add origin https://github.com/$username/$repo.git
        
        echo -e "${YELLOW}Would you like to push the initial commit to GitHub? (y/n)${NC}"
        read push
        
        if [ "$push" != "${push#[Yy]}" ]; then
            echo -e "Pushing to GitHub..."
            git push -u origin main
            echo -e "${GREEN}Repository pushed to GitHub successfully.${NC}"
        else
            echo -e "${BLUE}Skipping push to GitHub. You can push later with:${NC}"
            echo -e "  git push -u origin main"
        fi
    else
        echo -e "${BLUE}Skipping GitHub remote setup. You can set up later with:${NC}"
        echo -e "  git remote add origin https://github.com/CallMeChewy/OllamaModelEditor.git"
    fi
}

# Function to create Windows setup script
CreateWindowsScript() {
    PrintHeader "Creating Windows Setup Script"
    
    cat > scripts/Setup.bat << EOF
@echo off
REM File: Setup.bat
REM Path: OllamaModelEditor/scripts/Setup.bat
REM Standard: AIDEV-PascalCase-1.2
REM Created: 2025-03-11
REM Last Modified: 2025-03-11
REM Description: Windows setup script for OllamaModelEditor project

echo === Setting Up Python Virtual Environment ===
python -m venv .venv
call .venv\Scripts\activate.bat

echo === Installing Dependencies ===
pip install -r requirements.txt

echo === Setup Complete ===
echo.
echo Virtual environment created and dependencies installed.
echo To activate the virtual environment in the future, run:
echo   .venv\Scripts\activate.bat
echo.
pause
EOF
    
    chmod +x scripts/Setup.bat
    echo -e "${GREEN}Windows setup script created.${NC}"
}

# Function to create initial Main.py
CreateMainPy() {
    PrintHeader "Creating Main.py"
    
    cat > Main.py << EOF
# File: Main.py
# Path: OllamaModelEditor/Main.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Entry point for the OllamaModelEditor application

import sys
from pathlib import Path

# Add project root to path
ProjectRoot = Path(__file__).resolve().parent
sys.path.append(str(ProjectRoot))

# Import GUI components
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    from GUI.Windows.MainWindow import MainWindow
    from GUI.Windows.SplashScreen import SplashScreen
except ImportError:
    print("Error: PySide6 is required but not installed.")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)

# Import core components
from Core.LoggingUtils import SetupLogging
from Core.ConfigManager import ConfigManager

def Main():
    """Application entry point."""
    # Initialize logging
    SetupLogging()
    
    # Create application
    App = QApplication(sys.argv)
    App.setApplicationName("OllamaModelEditor")
    App.setOrganizationName("CallMeChewy")
    
    # Initialize configuration
    Config = ConfigManager()
    Config.LoadConfig()
    
    # Create and display splash screen
    Splash = SplashScreen()
    Splash.show()
    
    # Initialize main window
    MainWin = MainWindow(Config)
    
    # Close splash and show main window after delay
    QTimer.singleShot(2000, lambda: ShowMainWindow(Splash, MainWin))
    
    # Start event loop
    return App.exec()

def ShowMainWindow(Splash, MainWin):
    """Close splash screen and show main window."""
    Splash.finish(MainWin)
    MainWin.show()

if __name__ == "__main__":
    sys.exit(Main())
EOF
    
    echo -e "${GREEN}Main.py created successfully.${NC}"
}

# Function to create README.md
CreateReadme() {
    PrintHeader "Creating README.md"
    
    cat > README.md << EOF
# OLLAMA MODEL EDITOR

**A powerful tool for customizing and optimizing Ollama AI models**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation) • [Contributing](#contributing) • [License](#license)

## About

Ollama Model Editor is a comprehensive GUI application that allows you to customize, optimize, and manage your Ollama AI models. This tool provides an intuitive interface for adjusting model parameters, comparing performance across different configurations, and streamlining your AI workflow.

**This project is a collaboration between human developers and AI assistants, demonstrating the power of human-AI teamwork in software development.**

## Features

- 🎛️ **Parameter Customization**: Fine-tune model parameters through an intuitive GUI
- 📊 **Performance Benchmarking**: Compare different model configurations side-by-side
- 🔄 **Model Management**: Easily manage multiple Ollama models in one interface
- 🎯 **Optimization Presets**: Apply pre-configured optimization settings for specific use cases
- 📝 **Detailed Analysis**: Get insights into how parameter changes affect model performance
- 🌓 **Theming Support**: Choose between light and dark themes for comfortable usage
- 💾 **Configuration Export**: Share your optimized model configurations with others

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running on your system
- Git (for cloning the repository)

### Setup

```bash
# Clone the repository
git clone https://github.com/CallMeChewy/OllamaModelEditor.git
cd OllamaModelEditor

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python Main.py
```

## Usage

1. Launch the application with **python Main.py**
2. Select an Ollama model from the dropdown menu
3. Adjust parameters using the intuitive interface
4. Compare performance with different settings
5. Save your optimized configuration
6. Export settings to share with the community

For more detailed instructions, see the [Quick Start Guide](docs/QuickStartGuide.md).

## Documentation

- [Quick Start Guide](docs/QuickStartGuide.md)
- [Core Components](Core/README.md)
- [Parameter Reference](docs/parameters.md)
- [Advanced Usage](docs/advanced_usage.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (**git checkout -b feature/amazing-feature**)
3. Commit your changes (**git commit -m 'Add some amazing feature'**)
4. Push to the branch (**git push origin feature/amazing-feature**)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project is a collaboration between human developers and AI assistants
- Special thanks to the Ollama project for making powerful AI models accessible
- Developed by Herbert J. Bowers (Herb@BowersWorld.com)
EOF
    
    echo -e "${GREEN}README.md created successfully.${NC}"
}

# Function to create MIT license
CreateLicense() {
    PrintHeader "Creating LICENSE"
    
    cat > LICENSE << EOF
MIT License

Copyright (c) 2025 Herbert J. Bowers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
    
    echo -e "${GREEN}LICENSE created successfully.${NC}"
}

# Main execution
PrintHeader "OllamaModelEditor Project Setup"

# Check for required commands
CheckCommand "python3"
CheckCommand "git"

# Create project structure
CreateDirectories

# Setup tasks
SetupVirtualEnv
SetupGit
CreateWindowsScript
CreateMainPy
CreateReadme
CreateLicense
SetupGitHubRemote

PrintHeader "Setup Complete"
echo -e "${GREEN}OllamaModelEditor project has been successfully set up!${NC}"
echo -e "\nTo activate the virtual environment:"
echo -e "  ${BLUE}source .venv/bin/activate${NC}"
echo -e "\nTo start the application:"
echo -e "  ${BLUE}python Main.py${NC}"
echo -e "\nHappy coding! 🚀"
