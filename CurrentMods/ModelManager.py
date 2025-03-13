# File: ModelManager.py
# Path: OllamaModelEditor/Core/ModelManager.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-12 10:00PM
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
                
                # Recor