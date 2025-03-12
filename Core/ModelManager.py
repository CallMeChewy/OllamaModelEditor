# File: ModelManager.py
# Path: OllamaModelEditor/Core/ModelManager.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Manages Ollama model operations for the OllamaModelEditor application

import os
import json
import requests
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import logging

# Import project modules
from Core.ConfigManager import ConfigManager

class ModelManager:
    """Manages Ollama model operations and interactions."""
    
    def __init__(self, Config: ConfigManager):
        """
        Initialize the model manager.
        
        Args:
            Config: Configuration manager instance
        """
        self.Config = Config
        self.APIEndpoint = Config.GetAppConfig('APIEndpoint', 'http://localhost:11434/api')
        self.Logger = logging.getLogger('OllamaModelEditor.ModelManager')
        self.AvailableModels = []
        self.CurrentModel = None
    
    def GetAvailableModels(self) -> List[Dict[str, Any]]:
        """
        Retrieve list of available Ollama models.
        
        Returns:
            List of model information dictionaries
        """
        try:
            # Send request to Ollama API
            Response = requests.get(f"{self.APIEndpoint}/tags")
            
            if Response.status_code == 200:
                # Parse response and update available models
                ModelData = Response.json()
                self.AvailableModels = ModelData.get('models', [])
                return self.AvailableModels
            else:
                self.Logger.error(f"Failed to retrieve models: {Response.status_code}")
                return []
                
        except Exception as Error:
            self.Logger.error(f"Error retrieving models: {Error}")
            return []
    
    def GetModelDetails(self, ModelName: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            Dict containing model details or empty dict if not found
        """
        try:
            # First check if we need to fetch the latest models
            if not self.AvailableModels:
                self.GetAvailableModels()
            
            # Find model in available models
            for Model in self.AvailableModels:
                if Model.get('name') == ModelName:
                    # Get additional model information
                    Response = requests.post(
                        f"{self.APIEndpoint}/show",
                        json={"name": ModelName}
                    )
                    
                    if Response.status_code == 200:
                        # Combine basic and detailed model information
                        DetailedInfo = Response.json()
                        return {**Model, **DetailedInfo}
                    else:
                        self.Logger.error(f"Failed to get model details: {Response.status_code}")
                        return Model
            
            self.Logger.warning(f"Model not found: {ModelName}")
            return {}
                
        except Exception as Error:
            self.Logger.error(f"Error getting model details: {Error}")
            return {}
    
    def SetCurrentModel(self, ModelName: str) -> bool:
        """
        Set the current working model.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get model details
            ModelDetails = self.GetModelDetails(ModelName)
            
            if not ModelDetails:
                self.Logger.error(f"Cannot set current model: {ModelName} not found")
                return False
            
            # Set current model
            self.CurrentModel = ModelDetails
            
            # Add to recent models list
            self.Config.AddRecentModel(ModelName)
            
            return True
                
        except Exception as Error:
            self.Logger.error(f"Error setting current model: {Error}")
            return False
    
    def GetCurrentModel(self) -> Optional[Dict[str, Any]]:
        """
        Get the current working model.
        
        Returns:
            Dict containing current model details or None if not set
        """
        return self.CurrentModel
    
    def GenerateCompletion(self, Prompt: str, Parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a completion using the current model.
        
        Args:
            Prompt: Input prompt for generation
            Parameters: Optional parameter overrides
            
        Returns:
            Dict containing the response
        """
        try:
            if not self.CurrentModel:
                self.Logger.error("No current model set")
                return {"error": "No current model set"}
            
            # Get model name
            ModelName = self.CurrentModel.get('name')
            
            # Get model parameters with defaults
            ModelParams = self.Config.GetModelConfig(ModelName)
            
            # Override with provided parameters if any
            if Parameters:
                ModelParams.update(Parameters)
            
            # Prepare request
            RequestData = {
                "model": ModelName,
                "prompt": Prompt,
                "temperature": ModelParams.get('Temperature', 0.7),
                "top_p": ModelParams.get('TopP', 0.9),
                "max_tokens": ModelParams.get('MaxTokens', 2048),
                "frequency_penalty": ModelParams.get('FrequencyPenalty', 0.0),
                "presence_penalty": ModelParams.get('PresencePenalty', 0.0),
                "stream": False
            }
            
            # Send request to Ollama API
            Response = requests.post(
                f"{self.APIEndpoint}/generate",
                json=RequestData
            )
            
            if Response.status_code == 200:
                return Response.json()
            else:
                self.Logger.error(f"Generation failed: {Response.status_code}")
                return {"error": f"Generation failed: {Response.status_code}"}
                
        except Exception as Error:
            self.Logger.error(f"Error generating completion: {Error}")
            return {"error": str(Error)}
    
    def UpdateModelParameters(self, ModelName: str, Parameters: Dict[str, Any]) -> bool:
        """
        Update parameters for a specific model.
        
        Args:
            ModelName: Name of the model
            Parameters: New parameter values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current parameters
            CurrentParams = self.Config.GetModelConfig(ModelName)
            
            # Update parameters
            CurrentParams.update(Parameters)
            
            # Validate parameters
            if not self._ValidateParameters(CurrentParams):
                self.Logger.error("Invalid parameters")
                return False
            
            # Save updated parameters
            self.Config.SetModelConfig(ModelName, CurrentParams)
            
            # Save configuration
            self.Config.SaveConfig()
            
            return True
                
        except Exception as Error:
            self.Logger.error(f"Error updating model parameters: {Error}")
            return False
    
    def _ValidateParameters(self, Parameters: Dict[str, Any]) -> bool:
        """
        Validate model parameters.
        
        Args:
            Parameters: Parameters to validate
            
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        # Required parameters
        RequiredParams = ['Temperature', 'TopP', 'MaxTokens']
        
        # Check required parameters
        for Param in RequiredParams:
            if Param not in Parameters:
                self.Logger.error(f"Missing required parameter: {Param}")
                return False
        
        # Validate parameter ranges
        if not 0 <= Parameters.get('Temperature', 0) <= 2:
            self.Logger.error("Temperature must be between 0 and 2")
            return False
        
        if not 0 <= Parameters.get('TopP', 0) <= 1:
            self.Logger.error("TopP must be between 0 and 1")
            return False
        
        if Parameters.get('MaxTokens', 0) <= 0:
            self.Logger.error("MaxTokens must be greater than 0")
            return False
        
        return True
    
    def BenchmarkModel(self, ModelName: str, Prompts: List[str], Parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Benchmark model performance with provided prompts.
        
        Args:
            ModelName: Name of the model
            Prompts: List of test prompts
            Parameters: Optional parameter overrides
            
        Returns:
            Dict containing benchmark results
        """
        try:
            # Set current model if not already set
            if not self.CurrentModel or self.CurrentModel.get('name') != ModelName:
                if not self.SetCurrentModel(ModelName):
                    return {"error": f"Could not set model: {ModelName}"}
            
            # Initialize results
            Results = {
                "model": ModelName,
                "parameters": Parameters or self.Config.GetModelConfig(ModelName),
                "tests": [],
                "summary": {}
            }
            
            # Run tests for each prompt
            TotalTokens = 0
            TotalTime = 0
            
            for Index, Prompt in enumerate(Prompts):
                # Generate completion
                StartTime = time.time()
                Response = self.GenerateCompletion(Prompt, Parameters)
                EndTime = time.time()
                
                # Check for errors
                if "error" in Response:
                    Results["tests"].append({
                        "id": Index,
                        "prompt": Prompt,
                        "error": Response["error"]
                    })
                    continue
                
                # Calculate statistics
                ElapsedTime = EndTime - StartTime
                OutputTokens = Response.get("usage", {}).get("completion_tokens", 0)
                InputTokens = Response.get("usage", {}).get("prompt_tokens", 0)
                TotalPromptTokens = InputTokens + OutputTokens
                
                # Update totals
                TotalTokens += TotalPromptTokens
                TotalTime += ElapsedTime
                
                # Add test result
                Results["tests"].append({
                    "id": Index,
                    "prompt": Prompt,
                    "elapsed_time": ElapsedTime,
                    "input_tokens": InputTokens,
                    "output_tokens": OutputTokens,
                    "tokens_per_second": OutputTokens / ElapsedTime if ElapsedTime > 0 else 0
                })
            
            # Calculate summary statistics
            TestCount = len(Results["tests"])
            if TestCount > 0:
                Results["summary"] = {
                    "total_tests": TestCount,
                    "total_tokens": TotalTokens,
                    "total_time": TotalTime,
                    "average_tokens_per_second": TotalTokens / TotalTime if TotalTime > 0 else 0,
                    "average_time_per_test": TotalTime / TestCount
                }
            
            return Results
                
        except Exception as Error:
            self.Logger.error(f"Error benchmarking model: {Error}")
            return {"error": str(Error)}
    
    def ExportModelDefinition(self, ModelName: str, FilePath: str) -> bool:
        """
        Export model definition to a file.
        
        Args:
            ModelName: Name of the model
            FilePath: Path to save the definition
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get model details
            ModelDetails = self.GetModelDetails(ModelName)
            
            if not ModelDetails:
                self.Logger.error(f"Model not found: {ModelName}")
                return False
            
            # Get model parameters
            ModelParams = self.Config.GetModelConfig(ModelName)
            
            # Combine details and parameters
            ExportData = {
                "name": ModelName,
                "details": ModelDetails,
                "parameters": ModelParams
            }
            
            # Ensure directory exists
            Path(FilePath).parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(FilePath, 'w') as ExportFile:
                json.dump(ExportData, ExportFile, indent=2)
            
            return True
                
        except Exception as Error:
            self.Logger.error(f"Error exporting model definition: {Error}")
            return False
