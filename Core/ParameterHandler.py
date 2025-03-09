# File: ParameterHandler.py
# Path: OllamaModelEditor/Core/ParameterHandler.py
# Standard: AIDEV-PascalCase-1.0

import re
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union

class ParameterHandler:
    """Handles validation and documentation of Ollama model parameters."""
    
    def __init__(self, config_manager, logger):
        """Initialize the parameter handler.
        
        Args:
            config_manager: The configuration manager instance
            logger: The logger instance
        """
        self.Config = config_manager
        self.Logger = logger
        self.LastValidationError = ""
        
        # Load parameter documentation and constraints
        self.ParameterDocs = self._LoadParameterDocs()
    
    def _LoadParameterDocs(self) -> Dict[str, Any]:
        """Load parameter documentation and constraints.
        
        Returns:
            Dict[str, Any]: Dictionary of parameter documentation
        """
        # Define built-in parameter documentation
        # This could be loaded from a file in the future
        DocsData = {
            "temperature": {
                "description": "Controls randomness in the generation process",
                "type": "float",
                "min": 0.0,
                "max": 2.0,
                "default": 0.8,
                "help": "Higher values (e.g., 1.0) produce more random outputs, while lower values (e.g., 0.2) make outputs more focused and deterministic.",
                "caution": "Values above 1.2 may produce increasingly random and potentially nonsensical outputs.",
                "examples": [
                    "0.2 - Good for factual responses and code generation",
                    "0.8 - Good for general conversation",
                    "1.0 - Good for creative writing and brainstorming"
                ],
                "performance_impact": "Minimal impact on performance or resource usage."
            },
            "top_p": {
                "description": "Controls diversity via nucleus sampling",
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.9,
                "help": "The model considers the most likely tokens whose cumulative probability exceeds the top_p value. Lower values mean less randomness.",
                "examples": [
                    "0.5 - More deterministic responses",
                    "0.9 - Balanced between deterministic and diverse"
                ],
                "performance_impact": "Minimal impact on performance or resource usage."
            },
            "top_k": {
                "description": "Limits the next token selection to the K most probable tokens",
                "type": "int",
                "min": 0,
                "max": 100,
                "default": 40,
                "help": "The model selects from only the k most likely next tokens. Lower values increase focus but may reduce quality.",
                "examples": [
                    "0 - Disabled (uses all tokens)",
                    "20 - More focused outputs",
                    "40 - Balanced setting"
                ],
                "performance_impact": "Minimal impact on performance or resource usage."
            },
            "mirostat": {
                "description": "Enable Mirostat sampling for controlling perplexity",
                "type": "int",
                "options": [0, 1, 2],
                "default": 0,
                "help": "0 = Disabled, 1 = Mirostat, 2 = Mirostat 2.0. Algorithms that control perplexity during generation.",
                "examples": [
                    "0 - Disabled",
                    "1 - Enable Mirostat algorithm",
                    "2 - Enable Mirostat 2.0 algorithm (adaptive)"
                ],
                "performance_impact": "May slightly increase inference time."
            },
            "mirostat_eta": {
                "description": "Learning rate for Mirostat algorithm",
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.1,
                "help": "Controls adjustment speed of the Mirostat algorithm.",
                "examples": [
                    "0.1 - Default value",
                    "0.05 - More gradual adjustments"
                ],
                "performance_impact": "No significant impact."
            },
            "mirostat_tau": {
                "description": "Controls perplexity when using Mirostat",
                "type": "float",
                "min": 0.0,
                "max": 10.0,
                "default": 5.0,
                "help": "Target entropy, controlling perplexity of the generated text.",
                "examples": [
                    "5.0 - Default value",
                    "3.0 - More focused, less creative output"
                ],
                "performance_impact": "No significant impact."
            },
            "num_ctx": {
                "description": "Size of the context window for the model",
                "type": "int",
                "min": 512,
                "max": 32768,
                "default": 4096,
                "help": "The maximum number of tokens the model can use for context. Larger values allow the model to 'remember' more of the conversation but require more memory.",
                "caution": "Increasing context length significantly increases memory usage. Ensure your system has sufficient RAM.",
                "examples": [
                    "2048 - Reduced memory usage",
                    "4096 - Default for most models",
                    "8192 - Extended context for longer conversations"
                ],
                "performance_impact": "Larger values increase memory usage proportionally."
            },
            "num_predict": {
                "description": "Maximum number of tokens to predict",
                "type": "int",
                "min": -1,
                "max": 32768,
                "default": -1,
                "help": "Limits the number of tokens generated in the response. -1 means no limit (except context size).",
                "examples": [
                    "-1 - No limit",
                    "100 - Short response",
                    "500 - Medium response",
                    "2000 - Long response"
                ],
                "performance_impact": "Larger values increase generation time linearly."
            },
            "repeat_penalty": {
                "description": "Penalty for repeating tokens",
                "type": "float",
                "min": 0.0,
                "max": 2.0,
                "default": 1.1,
                "help": "Penalizes repeating the same tokens in the output. Higher values prevent repetition but may impact coherence.",
                "examples": [
                    "1.0 - No penalty",
                    "1.1 - Default slight penalty",
                    "1.2 - Stronger penalty for repetitive content"
                ],
                "performance_impact": "Minimal impact on performance."
            },
            "repeat_last_n": {
                "description": "Sets the context size for the repeat penalty",
                "type": "int",
                "min": 0,
                "max": 32768,
                "default": 64,
                "help": "The repeat penalty will be applied to the last N tokens. 0 means the entire context will be used.",
                "examples": [
                    "0 - Apply to entire context",
                    "64 - Default (apply to recent tokens only)"
                ],
                "performance_impact": "Larger values may slightly increase computation time."
            },
            "presence_penalty": {
                "description": "Penalty for tokens already present in the context",
                "type": "float",
                "min": -2.0,
                "max": 2.0,
                "default": 0.0,
                "help": "Penalizes tokens based on their presence in the text so far. Positive values encourage the model to talk about new topics.",
                "examples": [
                    "0.0 - No penalty (default)",
                    "0.5 - Moderate penalty to encourage new topics",
                    "-0.5 - Negative penalty (encourages repetition)"
                ],
                "performance_impact": "Minimal impact on performance."
            },
            "frequency_penalty": {
                "description": "Penalty for tokens based on frequency in the context",
                "type": "float",
                "min": -2.0,
                "max": 2.0,
                "default": 0.0,
                "help": "Penalizes tokens based on their frequency in the text so far. Positive values discourage repetition of the same words.",
                "examples": [
                    "0.0 - No penalty (default)",
                    "0.5 - Moderate penalty to reduce repetition",
                    "-0.5 - Negative penalty (encourages repetition)"
                ],
                "performance_impact": "Minimal impact on performance."
            },
            "num_gpu": {
                "description": "Number of GPUs to use for generation",
                "type": "int",
                "min": 0,
                "max": 8,
                "default": 1,
                "help": "Number of GPUs to use for computation. 0 uses CPU only.",
                "caution": "Setting this higher than the number of available GPUs may cause errors.",
                "examples": [
                    "0 - CPU only",
                    "1 - Use one GPU",
                    "2 - Use two GPUs in parallel"
                ],
                "performance_impact": "Directly impacts performance and resource usage."
            },
            "num_thread": {
                "description": "Number of CPU threads to use",
                "type": "int",
                "min": 0,
                "max": 64,
                "default": 4,
                "help": "Number of CPU threads to use for computation. 0 means use all available cores.",
                "examples": [
                    "0 - Use all available CPU cores",
                    "4 - Use 4 CPU threads",
                    "8 - Use 8 CPU threads"
                ],
                "performance_impact": "Directly impacts CPU usage and performance."
            },
            "seed": {
                "description": "RNG seed for reproducible outputs",
                "type": "int",
                "min": -1,
                "max": 2147483647,
                "default": -1,
                "help": "Random number generator seed for deterministic outputs. -1 means random seed.",
                "examples": [
                    "-1 - Random seed (different results each time)",
                    "42 - Fixed seed for reproducible results"
                ],
                "performance_impact": "No impact on performance."
            },
            "stop": {
                "description": "Sequences at which to stop generation",
                "type": "string",
                "default": "",
                "help": "Generation will stop when the specified sequence is produced. Multiple stop sequences can be set.",
                "multi_value": True,
                "examples": [
                    "\"\\n\" - Stop at newline",
                    "\"<end>\" - Stop at custom token",
                    "\"User:\" - Stop at user message marker"
                ],
                "performance_impact": "No significant impact on performance."
            },
            "tfs_z": {
                "description": "Tail free sampling parameter",
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 1.0,
                "help": "Tail free sampling focuses sampling on more probable tokens. 1.0 disables tail free sampling.",
                "examples": [
                    "1.0 - Disabled (default)",
                    "0.95 - Mild filtering of low probability tokens",
                    "0.5 - Aggressive filtering"
                ],
                "performance_impact": "Minimal impact on performance."
            },
            "num_batch": {
                "description": "Number of batches to generate simultaneously",
                "type": "int",
                "min": 1,
                "max": 2048,
                "default": 8,
                "help": "Number of tokens to generate in parallel. Higher values can speed up generation but use more memory.",
                "caution": "Setting this too high may cause out-of-memory errors.",
                "examples": [
                    "1 - Lowest memory usage",
                    "8 - Default (balanced)",
                    "32 - Faster generation, more memory usage"
                ],
                "performance_impact": "Higher values increase memory usage and can improve throughput."
            }
        }
        
        return DocsData
    
    def GetParameterNames(self) -> List[str]:
        """Get the list of all supported parameter names.
        
        Returns:
            List[str]: List of parameter names
        """
        return list(self.ParameterDocs.keys())
    
    def GetParameterInfo(self, param_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific parameter.
        
        Args:
            param_name: The parameter name
            
        Returns:
            Optional[Dict[str, Any]]: Parameter information or None if not found
        """
        return self.ParameterDocs.get(param_name.lower(), None)
    
    def ValidateParameterValue(self, param_name: str, value: str) -> bool:
        """Validate a parameter value against its constraints.
        
        Args:
            param_name: The parameter name
            value: The parameter value
            
        Returns:
            bool: True if valid, False otherwise
        """
        ParamInfo = self.GetParameterInfo(param_name.lower())
        
        if not ParamInfo:
            self.LastValidationError = f"Unknown parameter: {param_name}"
            return False
        
        # Handle different parameter types
        ParamType = ParamInfo.get("type", "string")
        
        try:
            if ParamType == "int":
                # Convert to int and check range
                IntValue = int(value)
                Min = ParamInfo.get("min", None)
                Max = ParamInfo.get("max", None)
                
                if Min is not None and IntValue < Min:
                    self.LastValidationError = f"Value must be at least {Min}"
                    return False
                
                if Max is not None and IntValue > Max:
                    self.LastValidationError = f"Value must be at most {Max}"
                    return False
                
            elif ParamType == "float":
                # Convert to float and check range
                FloatValue = float(value)
                Min = ParamInfo.get("min", None)
                Max = ParamInfo.get("max", None)
                
                if Min is not None and FloatValue < Min:
                    self.LastValidationError = f"Value must be at least {Min}"
                    return False
                
                if Max is not None and FloatValue > Max:
                    self.LastValidationError = f"Value must be at most {Max}"
                    return False
                
            # Check options if specified
            if "options" in ParamInfo:
                # Convert value to the appropriate type
                if ParamType == "int":
                    TypedValue = int(value)
                elif ParamType == "float":
                    TypedValue = float(value)
                else:
                    TypedValue = value
                
                if TypedValue not in ParamInfo["options"]:
                    Options = ", ".join(str(opt) for opt in ParamInfo["options"])
                    self.LastValidationError = f"Value must be one of: {Options}"
                    return False
                
        except ValueError:
            # Type conversion failed
            self.LastValidationError = f"Invalid {ParamType} value: {value}"
            return False
        
        # If we made it here, the value is valid
        return True
    
    def IsMultiValueParameter(self, param_name: str) -> bool:
        """Check if a parameter supports multiple values.
        
        Args:
            param_name: The parameter name
            
        Returns:
            bool: True if the parameter supports multiple values
        """
        ParamInfo = self.GetParameterInfo(param_name.lower())
        if not ParamInfo:
            return False
        
        return ParamInfo.get("multi_value", False)
    
    def GetLastValidationError(self) -> str:
        """Get the last validation error message.
        
        Returns:
            str: The last validation error message
        """
        return self.LastValidationError
    
    def FormatParameterValue(self, param_name: str, value: Any) -> str:
        """Format a parameter value for display or storage.
        
        Args:
            param_name: The parameter name
            value: The parameter value
            
        Returns:
            str: Formatted parameter value
        """
        ParamInfo = self.GetParameterInfo(param_name.lower())
        
        if not ParamInfo:
            return str(value)
        
        ParamType = ParamInfo.get("type", "string")
        
        if ParamType == "float":
            try:
                return f"{float(value):.6g}"
            except (ValueError, TypeError):
                return str(value)
        
        return str(value)
    
    def GetDefaultParameterValue(self, param_name: str) -> Any:
        """Get the default value for a parameter.
        
        Args:
            param_name: The parameter name
            
        Returns:
            Any: Default parameter value or None if not defined
        """
        ParamInfo = self.GetParameterInfo(param_name.lower())
        
        if not ParamInfo:
            return None
        
        return ParamInfo.get("default", None)
    
    def GetParameterGroups(self) -> Dict[str, List[str]]:
        """Get parameters organized by functional groups.
        
        Returns:
            Dict[str, List[str]]: Dictionary of parameter groups
        """
        # Group parameters by functionality
        Groups = {
            "Generation": [
                "temperature", "top_p", "top_k", "mirostat",
                "mirostat_eta", "mirostat_tau", "seed"
            ],
            "Context": [
                "num_ctx", "num_predict"
            ],
            "Repetition Control": [
                "repeat_penalty", "repeat_last_n", 
                "presence_penalty", "frequency_penalty"
            ],
            "Sequence Control": [
                "stop", "tfs_z"
            ],
            "Performance": [
                "num_gpu", "num_thread", "num_batch"
            ]
        }
        
        return Groups