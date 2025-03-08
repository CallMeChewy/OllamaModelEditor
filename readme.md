# Ollama Model Editor

A Python-based GUI application to simplify testing and modifying Ollama models.

## Features

- Select from locally installed Ollama models
- View and modify model parameters with validation
- Compare original and modified parameter values
- Parameter documentation and constraints displayed
- Create new models based on modified parameters
- View model history and changes
- Export and import parameter configurations
- View Modelfiles for installed models

## Requirements

- Python 3.8+
- Ollama installed and accessible in your PATH
- Required Python packages:
  - tkinter
  - pyyaml

## Installation

1. Ensure you have Ollama installed and working properly
2. Install required Python packages:

```bash
pip install pyyaml
```

3. Clone or download this repository
4. Run the application:

```bash
python ollama_model_editor.py
```

## Usage

### Selecting a Model

1. Choose a model from the dropdown list at the top of the application
2. The application will load the model's current parameters

### Modifying Parameters

1. Parameters are displayed in a scrollable grid with "Original Value" and "Changed Value" columns
2. Click on a parameter to see detailed information in the right panel
3. Enter new values in the "Changed Value" column
4. Type `.` + Enter in any parameter field to copy the original value
5. Parameters with set options will display as dropdown menus

### Creating a New Model

1. After modifying parameters, enter a name for the new model at the bottom of the application
2. Click "Create Model" to create a new model with your modifications
3. The application will validate all parameters before creating the model

### Additional Features

- **Refresh Models**: Refresh the list of installed Ollama models
- **View Model History**: See a history of models created with this application and their changes
- **View Modelfile**: View the Modelfile for the currently selected model
- **Export Configuration**: Save the current parameter changes to a YAML file
- **Import Configuration**: Load parameter changes from a previously exported YAML file

## Logs and History

The application maintains logs and model history in the following location:

```
~/.ollama_editor/
```

- `model_editor.log`: Application logs
- `model_history.yaml`: History of created models and their parameter changes

## Troubleshooting

If you encounter any issues:

1. Check the application logs at `~/.ollama_editor/model_editor.log`
2. Ensure Ollama is installed and working correctly
3. Verify you have the required Python packages installed

## Future Enhancements

- Support for creating models from GGUF files
- Support for TEMPLATE and SYSTEM modifications
- Direct comparison between different models
- Parameter presets for common use cases
- Batch parameter testing
- Performance metrics for different parameter combinations

## License

MIT
