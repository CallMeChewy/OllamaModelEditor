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
