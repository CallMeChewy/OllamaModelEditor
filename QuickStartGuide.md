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
