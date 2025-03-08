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
