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
