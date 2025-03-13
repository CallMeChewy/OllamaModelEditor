# File: ModelManager.py
# Path: OllamaModelEditor/Core/ModelManager.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-12 11:30PM
# Description: Manages Ollama model operations for the OllamaModelEditor application

import os
import json
import requests
import time
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
        
        # Get database reference from Config if available
        self.DB = getattr(Config, 'DB', None)
    
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
                        
                        # Store last accessed time in database if available
                        if self.DB:
                            # Check if model exists in database
                            ModelConfigs = self.DB.GetModelConfigs(ModelName)
                            if not ModelConfigs:
                                # Create default config for model
                                DefaultParams = self.Config.GetModelConfig('DefaultParameters')
                                self.DB.SaveModelConfig(ModelName, "Default", DefaultParams)
                        
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
            
            # Update last used timestamp in database if available
            if self.DB:
                # Update LastUsed timestamp
                self.DB.ExecuteNonQuery(
                    """
                    UPDATE ModelConfigs 
                    SET LastUsed = CURRENT_TIMESTAMP 
                    WHERE ModelName = ?
                    """,
                    (ModelName,)
                )
            
            self.Logger.info(f"Current model set to: {ModelName}")
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
            
            # Start timer for performance tracking
            StartTime = time.time()
            
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
            
            # Calculate elapsed time
            ElapsedTime = time.time() - StartTime
            
            if Response.status_code == 200:
                ResponseData = Response.json()
                
                # Add generation time to response
                ResponseData['generation_time'] = ElapsedTime
                
                # Record in history if database is available
                if self.DB:
                    # Extract metrics
                    Metrics = {
                        'InputTokens': ResponseData.get('prompt_eval_count', 0),
                        'OutputTokens': ResponseData.get('eval_count', 0),
                        'TotalTokens': ResponseData.get('prompt_eval_count', 0) + ResponseData.get('eval_count', 0),
                        'GenerationTime': ElapsedTime
                    }
                    
                    # Add to history
                    self.DB.AddGenerationHistory(
                        ModelName,
                        Prompt,
                        ResponseData.get('response', ''),
                        ModelParams,
                        Metrics
                    )
                
                return ResponseData
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
            
            # Save to database if available
            if self.DB:
                self.DB.SaveModelConfig(ModelName, "Default", CurrentParams)
            
            self.Logger.info(f"Model parameters updated for {ModelName}")
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
    
    def BenchmarkModel(self, ModelName: str, Prompts: List[str], 
                      Parameters: Optional[Dict[str, Any]] = None, 
                      Runs: int = 3) -> Dict[str, Any]:
        """
        Benchmark model performance with provided prompts.
        
        Args:
            ModelName: Name of the model
            Prompts: List of test prompts
            Parameters: Optional parameter overrides
            Runs: Number of runs per prompt
            
        Returns:
            Dict containing benchmark results
        """
        try:
            # Set current model if not already set
            if not self.CurrentModel or self.CurrentModel.get('name') != ModelName:
                if not self.SetCurrentModel(ModelName):
                    return {"error": f"Could not set model: {ModelName}"}
            
            # Get parameters (with overrides if provided)
            ModelParams = self.Config.GetModelConfig(ModelName)
            if Parameters:
                ModelParams.update(Parameters)
            
            # Initialize results
            Results = {
                "model": ModelName,
                "parameters": ModelParams,
                "tests": [],
                "summary": {}
            }
            
            # Run tests for each prompt
            TotalTokens = 0
            TotalTime = 0
            
            for Index, Prompt in enumerate(Prompts):
                # Initialize metrics for this prompt
                PromptTotalTime = 0
                PromptTotalTokens = 0
                PromptTotalOutputTokens = 0
                SuccessfulRuns = 0
                
                # Run multiple times for consistent results
                for Run in range(Runs):
                    # Generate completion
                    Response = self.GenerateCompletion(Prompt, ModelParams)
                    
                    # Check for errors
                    if "error" in Response:
                        continue
                    
                    # Extract metrics
                    PromptTotalTime += Response.get('generation_time', 0)
                    InputTokens = Response.get('prompt_eval_count', 0)
                    OutputTokens = Response.get('eval_count', 0)
                    PromptTotalTokens += InputTokens + OutputTokens
                    PromptTotalOutputTokens += OutputTokens
                    
                    SuccessfulRuns += 1
                
                # Skip if all runs failed
                if SuccessfulRuns == 0:
                    Results["tests"].append({
                        "id": Index,
                        "prompt": Prompt,
                        "error": "All benchmark runs failed"
                    })
                    continue
                
                # Calculate averages
                AverageTime = PromptTotalTime / SuccessfulRuns
                AverageTokens = PromptTotalTokens / SuccessfulRuns
                AverageOutputTokens = PromptTotalOutputTokens / SuccessfulRuns
                TokensPerSecond = AverageOutputTokens / AverageTime if AverageTime > 0 else 0
                
                # Update totals
                TotalTokens += PromptTotalTokens
                TotalTime += PromptTotalTime
                
                # Add test result
                Results["tests"].append({
                    "id": Index,
                    "prompt": Prompt,
                    "average_time": AverageTime,
                    "average_tokens": AverageTokens,
                    "average_output_tokens": AverageOutputTokens,
                    "tokens_per_second": TokensPerSecond,
                    "successful_runs": SuccessfulRuns
                })
                
                # Save to database if available
                if self.DB:
                    self.DB.AddBenchmarkResult(
                        f"Prompt-{Index}",
                        ModelName,
                        Prompt,
                        AverageTime,
                        AverageTokens,
                        TokensPerSecond,
                        SuccessfulRuns,
                        ModelParams
                    )
            
            # Calculate summary statistics
            TestCount = len(Results["tests"])
            if TestCount > 0:
                Results["summary"] = {
                    "total_tests": TestCount,
                    "total_tokens": TotalTokens,
                    "total_time": TotalTime,
                    "average_tokens_per_second": TotalTokens / TotalTime if TotalTime > 0 else 0,
                    "average_time_per_test": TotalTime / TestCount,
                    "benchmark_date": time.strftime("%Y-%m-%d %H:%M:%S")
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
            
            # Get benchmark results if available
            BenchmarkResults = []
            if self.DB:
                BenchmarkResults = self.DB.GetBenchmarkResults(ModelName)
            
            # Combine details, parameters, and benchmarks
            ExportData = {
                "name": ModelName,
                "details": ModelDetails,
                "parameters": ModelParams,
                "benchmarks": BenchmarkResults
            }
            
            # Ensure directory exists
            Path(FilePath).parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(FilePath, 'w') as ExportFile:
                json.dump(ExportData, ExportFile, indent=2)
            
            self.Logger.info(f"Model definition exported to {FilePath}")
            return True
                
        except Exception as Error:
            self.Logger.error(f"Error exporting model definition: {Error}")
            return False
    
    def GetModelHistory(self, ModelName: str, Limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get generation history for a model.
        
        Args:
            ModelName: Name of the model
            Limit: Maximum number of entries to retrieve
            
        Returns:
            List of history entries
        """
        if self.DB:
            return self.DB.GetGenerationHistoryForModel(ModelName, Limit)
        
        return []
    
    def GetModelBenchmarks(self, ModelName: str) -> List[Dict[str, Any]]:
        """
        Get benchmark results for a model.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            List of benchmark results
        """
        if self.DB:
            return self.DB.GetBenchmarkResults(ModelName)
        
        return []
    
    def ApplyPreset(self, ModelName: str, PresetName: str) -> bool:
        """
        Apply a parameter preset to a model.
        
        Args:
            ModelName: Name of the model
            PresetName: Name of the preset
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get preset parameters
            PresetParams = None
            
            if self.DB:
                # Try to get from database
                Preset = self.DB.GetPreset(PresetName)
                if Preset:
                    PresetParams = {
                        'Temperature': Preset['Temperature'],
                        'TopP': Preset['TopP'],
                        'MaxTokens': Preset['MaxTokens'],
                        'FrequencyPenalty': Preset['FrequencyPenalty'],
                        'PresencePenalty': Preset['PresencePenalty']
                    }
                    
                    # Update preset usage statistics
                    self.DB.UpdatePresetUsage(PresetName)
            
            # Fall back to hardcoded presets if not found
            if not PresetParams:
                # Define presets
                Presets = {
                    "Default": {
                        'Temperature': 0.7,
                        'TopP': 0.9,
                        'MaxTokens': 2048,
                        'FrequencyPenalty': 0.0,
                        'PresencePenalty': 0.0
                    },
                    "Creative": {
                        'Temperature': 1.0,
                        'TopP': 0.95,
                        'MaxTokens': 4096,
                        'FrequencyPenalty': 0.0,
                        'PresencePenalty': 0.0
                    },
                    "Precise": {
                        'Temperature': 0.3,
                        'TopP': 0.7,
                        'MaxTokens': 2048,
                        'FrequencyPenalty': 0.5,
                        'PresencePenalty': 0.0
                    },
                    "Fast": {
                        'Temperature': 0.7,
                        'TopP': 0.9,
                        'MaxTokens': 1024,
                        'FrequencyPenalty': 0.0,
                        'PresencePenalty': 0.0
                    }
                }
                
                if PresetName in Presets:
                    PresetParams = Presets[PresetName]
                else:
                    self.Logger.error(f"Preset not found: {PresetName}")
                    return False
            
            # Apply preset parameters
            return self.UpdateModelParameters(ModelName, PresetParams)
        
        except Exception as Error:
            self.Logger.error(f"Error applying preset: {Error}")
            return False
    
    def SaveUserPreset(self, PresetName: str, Description: str, Parameters: Dict[str, Any]) -> bool:
        """
        Save a user-defined preset.
        
        Args:
            PresetName: Name of the preset
            Description: Preset description
            Parameters: Preset parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate parameters
            if not self._ValidateParameters(Parameters):
                self.Logger.error("Invalid parameters for preset")
                return False
            
            # Save to database if available
            if self.DB:
                self.DB.SaveUserPreset(PresetName, Description, Parameters)
                self.Logger.info(f"User preset '{PresetName}' saved")
                return True
            
            # No database, cannot save user preset
            self.Logger.error("Database not available, cannot save user preset")
            return False
            
        except Exception as Error:
            self.Logger.error(f"Error saving user preset: {Error}")
            return False
    
    def GetUserPresets(self) -> List[Dict[str, Any]]:
        """
        Get all user-defined presets.
        
        Returns:
            List of preset dictionaries
        """
        if self.DB:
            UserPresets = self.DB.GetUserPresets()
            
            # Convert database format to application format
            return [{
                'Name': Preset['Name'],
                'Description': Preset['Description'],
                'Parameters': {
                    'Temperature': Preset['Temperature'],
                    'TopP': Preset['TopP'],
                    'MaxTokens': Preset['MaxTokens'],
                    'FrequencyPenalty': Preset['FrequencyPenalty'],
                    'PresencePenalty': Preset['PresencePenalty']
                }
            } for Preset in UserPresets]
        
        return []
    
    def DeleteUserPreset(self, PresetName: str) -> bool:
        """
        Delete a user-defined preset.
        
        Args:
            PresetName: Name of the preset
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.DB:
            Result = self.DB.DeleteUserPreset(PresetName)
            if Result:
                self.Logger.info(f"User preset '{PresetName}' deleted")
            else:
                self.Logger.warning(f"Failed to delete user preset '{PresetName}'")
            return Result
        
        return False
