# File: ParameterStateManager.py
# Path: OllamaModelEditor/Core/ParameterStateManager.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-13
# Last Modified: 2025-03-13
# Description: Manages parameter state tracking for the OllamaModelEditor application

from typing import Dict, Any, Optional, List, Tuple
import logging
import json
import copy
from pathlib import Path

class ParameterStateManager:
    """Manages and tracks parameter states for models."""
    
    def __init__(self, ModelManager, ConfigManager):
        """
        Initialize the parameter state manager.
        
        Args:
            ModelManager: Model manager instance
            ConfigManager: Configuration manager instance
        """
        self.Logger = logging.getLogger('OllamaModelEditor.ParameterStateManager')
        self.ModelManager = ModelManager
        self.ConfigManager = ConfigManager
        
        # Store original and current parameter states
        self.OriginalStates = {}  # ModelName -> Original parameters
        self.CurrentStates = {}   # ModelName -> Current parameters
        
        # Store model file contents (if available)
        self.ModelFiles = {}      # ModelName -> Model file content
    
    def LoadModelState(self, ModelName: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Load and track the state for a model.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            Tuple of (original state, current state)
        """
        # Get model details
        ModelDetails = self.ModelManager.GetModelDetails(ModelName)
        
        # Get model parameters from configuration
        ModelParams = self.ConfigManager.GetModelConfig(ModelName)
        
        # Store original state if not already stored
        if ModelName not in self.OriginalStates:
            self.OriginalStates[ModelName] = copy.deepcopy(ModelParams)
        
        # Update current state
        self.CurrentStates[ModelName] = copy.deepcopy(ModelParams)
        
        # Attempt to load model file content if available
        self._LoadModelFile(ModelName)
        
        return (self.OriginalStates[ModelName], self.CurrentStates[ModelName])
    
    def _LoadModelFile(self, ModelName: str) -> None:
        """
        Attempt to load the model file content.
        
        Args:
            ModelName: Name of the model
        """
        try:
            # Look for model file in standard Ollama locations
            HomeDir = Path.home()
            OllamaDir = HomeDir / '.ollama'
            
            # Check for model file in models directory
            ModelFile = OllamaDir / 'models' / f"{ModelName}.json"
            if not ModelFile.exists():
                # Try alternative path format
                ModelName = ModelName.replace(':', '_')
                ModelFile = OllamaDir / 'models' / f"{ModelName}.json"
            
            if ModelFile.exists():
                with open(ModelFile, 'r') as f:
                    self.ModelFiles[ModelName] = json.load(f)
                    self.Logger.info(f"Loaded model file for {ModelName}")
            else:
                self.Logger.info(f"Model file not found for {ModelName}")
        except Exception as Error:
            self.Logger.error(f"Error loading model file for {ModelName}: {Error}")
    
    def UpdateCurrentState(self, ModelName: str, Parameters: Dict[str, Any]) -> None:
        """
        Update the current state for a model.
        
        Args:
            ModelName: Name of the model
            Parameters: Updated parameters
        """
        # Ensure model state is loaded
        if ModelName not in self.CurrentStates:
            self.LoadModelState(ModelName)
        
        # Update current state
        self.CurrentStates[ModelName].update(Parameters)
    
    def GetStateDifferences(self, ModelName: str) -> Dict[str, Tuple[Any, Any]]:
        """
        Get differences between original and current states.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            Dictionary mapping parameter names to (original, current) value tuples
        """
        if ModelName not in self.OriginalStates or ModelName not in self.CurrentStates:
            return {}
        
        Differences = {}
        Original = self.OriginalStates[ModelName]
        Current = self.CurrentStates[ModelName]
        
        # Find all parameter keys from both states
        AllParams = set(Original.keys()) | set(Current.keys())
        
        for Param in AllParams:
            OrigValue = Original.get(Param)
            CurrValue = Current.get(Param)
            
            if OrigValue != CurrValue:
                Differences[Param] = (OrigValue, CurrValue)
        
        return Differences
    
    def GetModelFile(self, ModelName: str) -> Optional[Dict[str, Any]]:
        """
        Get the model file content if available.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            Dictionary containing model file content or None if not available
        """
        return self.ModelFiles.get(ModelName)
    
    def GetAllModelParameters(self, ModelName: str) -> Dict[str, Any]:
        """
        Get all available parameters for a model.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            Dictionary containing all available parameters
        """
        # Start with current state parameters
        AllParams = copy.deepcopy(self.CurrentStates.get(ModelName, {}))
        
        # Add parameters from model file if available
        ModelFile = self.GetModelFile(ModelName)
        if ModelFile and 'parameters' in ModelFile:
            # Get parameters from model file
            FileParams = ModelFile.get('parameters', {})
            
            # Add missing parameters
            for Param, Value in FileParams.items():
                if Param not in AllParams:
                    AllParams[Param] = Value
        
        return AllParams
    
    def ResetToOriginal(self, ModelName: str) -> Dict[str, Any]:
        """
        Reset current state to original state.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            Dictionary containing original parameters
        """
        if ModelName in self.OriginalStates:
            self.CurrentStates[ModelName] = copy.deepcopy(self.OriginalStates[ModelName])
            return self.CurrentStates[ModelName]
        return {}
    
    def CommitCurrentState(self, ModelName: str) -> bool:
        """
        Commit current state as the new original state.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        if ModelName in self.CurrentStates:
            # Save current state to configuration
            self.ConfigManager.SetModelConfig(ModelName, self.CurrentStates[ModelName])
            
            # Update original state
            self.OriginalStates[ModelName] = copy.deepcopy(self.CurrentStates[ModelName])
            
            self.Logger.info(f"Committed current state for {ModelName}")
            return True
        
        self.Logger.error(f"Cannot commit state for {ModelName}: no current state")
        return False
