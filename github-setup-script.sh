#!/bin/bash
# GitHub repository setup script for OllamaModelEditor

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}Setting up OllamaModelEditor GitHub Repository...${RESET}\n"

# Create .gitignore file
echo -e "${YELLOW}Creating .gitignore file...${RESET}"
cat > .gitignore << 'EOF'
# Python virtual environments
.venv/
venv/
env/
ENV/

# Custom exclusions
..Exclude/

# Python bytecode
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Distribution / packaging
dist/
build/
*.egg-info/

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover

# Logs
*.log
logs/

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE specific files
.idea/
.vscode/
*.swp
*.swo

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF

# Create enhanced README.md with banner
echo -e "${YELLOW}Creating enhanced README.md...${RESET}"
cat > README.md << 'EOF'
<div align="center">
  <img src="docs/images/ollama_model_editor_banner.png" alt="Ollama Model Editor" width="600">
  <h1>Ollama Model Editor</h1>
  <p><strong>A powerful tool for customizing and optimizing Ollama AI models</strong></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#documentation">Documentation</a> •
    <a href="#contributing">Contributing</a> •
    <a href="#license">License</a>
  </p>
</div>

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
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python Main.py
```

## Usage

1. Launch the application with `python Main.py`
2. Select an Ollama model from the dropdown menu
3. Adjust parameters using the intuitive interface
4. Compare performance with different settings
5. Save your optimized configuration
6. Export settings to share with the community

For more detailed instructions, see the [Quick Start Guide](QuickStartGuide.md).

## Documentation

- [Quick Start Guide](QuickStartGuide.md)
- [Core Components](Core/README.md)
- [Parameter Reference](docs/parameters.md)
- [Advanced Usage](docs/advanced_usage.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project is a collaboration between human developers and AI assistants
- Special thanks to the Ollama project for making powerful AI models accessible
- Icons provided by [name of icon provider]
EOF

# Create MIT LICENSE file
echo -e "${YELLOW}Creating LICENSE file...${RESET}"
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 CallMeChewy

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

# Create Core/README.md with better content
echo -e "${YELLOW}Enhancing Core/README.md...${RESET}"
cat > Core/README.md << 'EOF'
# Core Components

This directory contains the core functionality of the Ollama Model Editor.

## Components

### ConfigManager.py
Handles configuration loading and saving, using YAML for persistent storage of application settings.

### LoggingUtils.py
Provides standardized logging functionality throughout the application.

### ModelManager.py
Core component responsible for interfacing with Ollama, managing model configurations, and tracking parameters.

### ParameterHandler.py
Processes and validates model parameters, ensuring they meet the requirements for Ollama models.

## Architecture

The Core components are designed to be independent of the UI layer, allowing for potential headless operation or alternative interfaces in the future.

```
ConfigManager → ModelManager ↔ ParameterHandler
       ↑              ↑
       └──────────────┴── LoggingUtils
```

## Usage Examples

```python
from Core.ConfigManager import ConfigManager
from Core.ModelManager import ModelManager

# Load configuration
config = ConfigManager().load_config()

# Initialize model manager
model_manager = ModelManager(config)

# Get available models
models = model_manager.get_available_models()

# Get model parameters
parameters = model_manager.get_model_parameters("llama3")
```
EOF

# Create enhanced QuickStartGuide.md
echo -e "${YELLOW}Enhancing QuickStartGuide.md...${RESET}"
cat > QuickStartGuide.md << 'EOF'
# Quick Start Guide

Welcome to Ollama Model Editor! This guide will help you get started quickly.

## Installation

1. **Prerequisites**:
   - Python 3.8 or higher
   - Ollama installed and running on your system
   - Git (for cloning the repository)

2. **Clone and setup**:
   ```bash
   git clone https://github.com/CallMeChewy/OllamaModelEditor.git
   cd OllamaModelEditor
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Launch the application**:
   ```bash
   python Main.py
   ```

## Basic Usage

### 1. Connect to Ollama

When you start the application, it will automatically attempt to connect to Ollama running on your local machine. If Ollama is running on a different host, you can change the connection settings in the Configuration menu.

### 2. Select a Model

From the main window, select an Ollama model from the dropdown menu. The application will load the current parameters for the selected model.

### 3. Adjust Parameters

Use the Parameter Panel to adjust various model parameters:
- **Context Length**: Modify the context window size
- **Temperature**: Adjust randomness in responses
- **Top-P**: Control diversity in token selection
- **Advanced Parameters**: Access more specialized settings

### 4. Compare Configurations

Use the Comparison Tool to:
1. Create named configurations
2. Run benchmark tests across configurations
3. View side-by-side results

### 5. Save and Export

- Save your configuration for future use
- Export your settings to share with others
- Apply your configuration to the Ollama model

## Tips and Tricks

- **Reset to Defaults**: Use the "Reset" button to return to default parameters
- **Parameter Descriptions**: Hover over parameter names for detailed descriptions
- **Dark Mode**: Toggle dark mode in the View menu for late-night editing
- **Parameter Presets**: Try the built-in presets for common use cases

## Next Steps

Once you're familiar with the basics, explore these advanced features:
- Creating custom parameter presets
- Batch testing multiple configurations
- Exporting performance reports
- Automated optimization

For more detailed information, refer to the [full documentation](docs/index.md).
EOF

# Create docs directory with additional documentation
echo -e "${YELLOW}Creating docs directory structure...${RESET}"
mkdir -p docs/images

# Create a parameters.md file in docs
cat > docs/parameters.md << 'EOF'
# Parameter Reference

This document provides detailed information about the parameters that can be adjusted in the Ollama Model Editor.

## Core Parameters

### Temperature
- **Range**: 0.0 - 2.0
- **Default**: 0.8
- **Description**: Controls randomness in the model's output. Higher values (e.g., 1.0) make output more random, while lower values (e.g., 0.2) make it more focused and deterministic.
- **Use Cases**: Lower for factual/coding tasks, higher for creative writing.

### Top P (Nucleus Sampling)
- **Range**: 0.0 - 1.0
- **Default**: 0.9
- **Description**: Controls diversity of model output. The model considers the most likely tokens whose cumulative probability exceeds the top_p value.
- **Use Cases**: Lower values (0.5) for more focused output, higher (0.95) for more diverse output.

### Top K
- **Range**: 0 - 100
- **Default**: 40
- **Description**: Limits the model to consider only the top k most likely tokens at each step.
- **Use Cases**: Lower values increase focus but may reduce creativity.

### Context Length / Context Window
- **Range**: Model dependent (typically 2048 - 32768)
- **Default**: Model dependent
- **Description**: Maximum number of tokens the model considers from previous conversation.
- **Use Cases**: Larger values allow for longer conversations but require more memory.

## Advanced Parameters

### Repeat Penalty
- **Range**: 0.0 - 2.0
- **Default**: 1.1
- **Description**: Penalizes the model for repeating the same words or phrases.
- **Use Cases**: Increase to reduce repetitive outputs.

### Presence Penalty
- **Range**: -2.0 - 2.0
- **Default**: 0.0
- **Description**: Penalizes new tokens based on their presence in the text so far.
- **Use Cases**: Positive values encourage the model to talk about new topics.

### Frequency Penalty
- **Range**: -2.0 - 2.0
- **Default**: 0.0
- **Description**: Penalizes new tokens based on their frequency in the text so far.
- **Use Cases**: Positive values discourage the model from repeating the same line multiple times.

### Mirostat
- **Range**: 0 - 2
- **Default**: 0 (disabled)
- **Description**: Enables Mirostat sampling for controlling perplexity.
- **Use Cases**: Enable for more consistent creative text generation.

### Mirostat Tau
- **Range**: 0.0 - 10.0
- **Default**: 5.0
- **Description**: Controls perplexity when Mirostat is enabled.
- **Use Cases**: Adjust for different types of content generation.

### Mirostat Eta
- **Range**: 0.0 - 1.0
- **Default**: 0.1
- **Description**: Learning rate for Mirostat algorithm.

## Performance Parameters

### Num Batch
- **Range**: 1 - 2048
- **Default**: Model dependent
- **Description**: Number of tokens to predict in parallel.
- **Use Cases**: Higher values increase throughput but use more memory.

### Num GPU
- **Range**: 0 - available GPUs
- **Default**: 1
- **Description**: Number of GPUs to use for generation.
- **Use Cases**: Increase for better performance on multi-GPU systems.

### Num Thread
- **Range**: 0 - available CPU threads
- **Default**: System dependent
- **Description**: Number of CPU threads to use.
- **Use Cases**: Adjust based on your system's capabilities.

## Recommended Combinations

### Creative Writing
- Temperature: 0.9
- Top P: 0.95
- Repeat Penalty: 1.2
- Frequency Penalty: 0.1

### Coding Assistant
- Temperature: 0.2
- Top P: 0.6
- Repeat Penalty: 1.0
- Frequency Penalty: 0.0

### Balanced Conversation
- Temperature: 0.7
- Top P: 0.9
- Repeat Penalty: 1.1
- Frequency Penalty: 0.05
EOF

# Create advanced_usage.md in docs
cat > docs/advanced_usage.md << 'EOF'
# Advanced Usage Guide

This document covers advanced features and usage patterns for the Ollama Model Editor.

## Custom Parameter Presets

### Creating Custom Presets

You can create custom parameter presets to quickly switch between different configurations:

1. Adjust parameters to your desired values
2. Click "Save Preset" in the File menu
3. Name your preset and add a description
4. Access your presets from the Presets menu

### Sharing Presets

Presets can be exported and shared with other users:

```bash
# Export a preset to a file
File > Export Preset > Select Preset > Save

# Import a preset from a file
File > Import Preset > Select File
```

## Benchmarking

### Setting Up Benchmarks

1. Navigate to Tools > Benchmarking
2. Select models and configurations to benchmark
3. Choose benchmark type:
   - Generation Speed (tokens/second)
   - Response Quality (requires reference data)
   - Memory Usage
4. Run the benchmark and view results

### Interpreting Results

The benchmark results include:
- Performance metrics for each configuration
- Comparative analysis across configurations
- Resource usage statistics
- Recommendations for optimization

## Batch Operations

### Batch Configuration Testing

Test multiple parameter combinations at once:

1. Go to Tools > Batch Configuration
2. Set parameter ranges to test
3. Configure test prompt(s)
4. Run batch test
5. Review results and select optimal configuration

### Batch Model Management

Manage multiple models at once:

1. Go to Tools > Batch Management
2. Select multiple models
3. Apply configuration changes to all selected models
4. Pull/Remove multiple models

## Advanced Optimization

### Using the AI Advisor

The AI Advisor can analyze your usage patterns and suggest optimal parameters:

1. Enable usage logging in Settings
2. Use the application normally for a period of time
3. Open Tools > AI Advisor
4. Review and apply recommendations

### Parameter Sensitivity Analysis

Understand how each parameter affects performance:

1. Go to Tools > Sensitivity Analysis
2. Select a base configuration
3. Choose parameters to analyze
4. Run the analysis
5. View impact charts for each parameter

## Command-Line Interface

For automation and scripting, you can use the command-line interface:

```bash
# Apply a configuration to a model
python -m OllamaModelEditor --model llama3 --apply-config my_config.yaml

# Run a benchmark
python -m OllamaModelEditor --benchmark --models llama3,phi3 --config benchmark_settings.yaml

# Export a model's current configuration
python -m OllamaModelEditor --model llama3 --export-config
```

## Configuration File Reference

The application uses YAML configuration files with the following structure:

```yaml
application:
  theme: "dark"
  log_level: "info"
  ollama_host: "http://localhost:11434"

models:
  llama3:
    temperature: 0.7
    top_p: 0.9
    repeat_penalty: 1.1
  phi3:
    temperature: 0.5
    top_p: 0.8
    repeat_penalty: 1.2

presets:
  creative:
    description: "Settings for creative writing"
    parameters:
      temperature: 0.9
      top_p: 0.95
      repeat_penalty: 1.2
  coding:
    description: "Settings for code generation"
    parameters:
      temperature: 0.2
      top_p: 0.6
      repeat_penalty: 1.0
```
EOF

# Create a placeholder for the banner image
echo -e "${YELLOW}Creating placeholder for banner image...${RESET}"
mkdir -p docs/images
cat > docs/images/banner_placeholder.txt << 'EOF'
To complete the setup, you'll need to create a banner image for the project.
Consider creating a banner with the project name "Ollama Model Editor" and a relevant icon or graphic.
The recommended size is 1200x300 pixels.
Save it as "ollama_model_editor_banner.png" in this directory.
EOF

# Instructions for GitHub setup
echo -e "\n${GREEN}Files and directories set up successfully!${RESET}"
echo -e "\n${BOLD}Next steps for GitHub setup:${RESET}"
echo -e "1. Create a new ${BOLD}private${RESET} repository at ${YELLOW}https://github.com/new${RESET} with the name 'OllamaModelEditor'"
echo -e "2. Run the following commands to initialize and push to GitHub:\n"
echo -e "${YELLOW}git init${RESET}"
echo -e "${YELLOW}git add .${RESET}"
echo -e "${YELLOW}git commit -m \"Initial commit\"${RESET}"
echo -e "${YELLOW}git branch -M main${RESET}"
echo -e "${YELLOW}git remote add origin https://github.com/CallMeChewy/OllamaModelEditor.git${RESET}"
echo -e "${YELLOW}git push -u origin main${RESET}"
echo -e "\n3. Don't forget to create a banner image and replace ${BOLD}docs/images/ollama_model_editor_banner.png${RESET}"
echo -e "\n${GREEN}Your project is now ready for GitHub!${RESET}"
