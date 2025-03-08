# File: ModelManager.py
# Path: OllamaModelEditor/Core/ModelManager.py
# Standard: AIDEV-PascalCase-1.0

import os
import re
import yaml
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

class ModelManager:
    """Manages Ollama models and their parameters."""
    
    def __init__(self, ollama_interface, logger):
        """Initialize the model manager.
        
        Args:
            ollama_interface: Interface for communicating with Ollama
            logger: Logger instance for logging
        """
        self.OllamaInterface = ollama_interface
        self.Logger = logger
        self.ModelList = []
        self.ModelDetails = {}
        self.ModelParameters = {}
        self.ModelHistory = {}
        
        # Load model history if available
        self.LoadModelHistory()
    
    def GetModelList(self) -> List[str]:
        """Get the list of available Ollama models.
        
        Returns:
            List[str]: List of model names
        """
        Models = self.OllamaInterface.ListModels()
        self.ModelList = Models
        self.Logger.info(f"Found {len(Models)} models")
        return Models
    
    def GetModelDetails(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict[str, Any]: Dictionary of model details
        """
        if model_name in self.ModelDetails:
            return self.ModelDetails[model_name]
        
        Details = self.OllamaInterface.ShowModel(model_name)
        self.ModelDetails[model_name] = Details
        self.Logger.info(f"Loaded details for model {model_name}")
        return Details
    
    def GetModelParameters(self, model_name: str) -> Dict[str, Any]:
        """Get parameters for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict[str, Any]: Dictionary of model parameters
        """
        if model_name in self.ModelParameters:
            return self.ModelParameters[model_name]
        
        Modelfile = self.OllamaInterface.ShowModelfile(model_name)
        Parameters = self.ParseModelfileParameters(Modelfile)
        self.ModelParameters[model_name] = Parameters
        self.Logger.info(f"Loaded parameters for model {model_name}")
        return Parameters
    
    def ParseModelfileParameters(self, modelfile: str) -> Dict[str, Any]:
        """Parse parameters from a modelfile string.
        
        Args:
            modelfile: Modelfile content as string
            
        Returns:
            Dict[str, Any]: Dictionary of parameters
        """
        Parameters = {}
        MultiValueParams = {}
        
        for Line in modelfile.split("\n"):
            if Line.strip().upper().startswith("PARAMETER "):
                Parts = Line.strip()[10:].split(" ", 1)
                if len(Parts) == 2:
                    ParamName, ParamValue = Parts
                    ParamName = ParamName.lower()
                    
                    # Check if this is a multi-value parameter (like stop)
                    if ParamName in Parameters:
                        # If we already have this parameter, handle as multi-value
                        if ParamName not in MultiValueParams:
                            MultiValueParams[ParamName] = [Parameters[ParamName]]
                        MultiValueParams[ParamName].append(ParamValue)
                    else:
                        Parameters[ParamName] = ParamValue
        
        # Process multi-value parameters
        for ParamName, Values in MultiValueParams.items():
            Parameters[ParamName] = Values
        
        return Parameters
    
    def GetModelfile(self, model_name: str) -> str:
        """Get the modelfile content for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            str: The modelfile content
        """
        return self.OllamaInterface.ShowModelfile(model_name)
    
    def CreateModel(self, new_name: str, base_model: str, parameters: Dict[str, Any]) -> bool:
        """Create a new model with specified parameters.
        
        Args:
            new_name: Name for the new model
            base_model: Base model to build from
            parameters: Dictionary of parameters to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create Modelfile content
            ModelfileContent = f"FROM {base_model}\n\n"
            
            # Process parameters
            for ParamName, Value in parameters.items():
                if isinstance(Value, list):
                    # Handle multi-value parameters
                    for Val in Value:
                        ModelfileContent += f"PARAMETER {ParamName} {Val}\n"
                else:
                    ModelfileContent += f"PARAMETER {ParamName} {Value}\n"
            
            # Create the model
            Success = self.OllamaInterface.CreateModel(new_name, ModelfileContent)
            
            if Success:
                # Log the model creation
                self.LogModelCreation(new_name, base_model, parameters)
                self.Logger.info(f"Created model {new_name} based on {base_model}")
                return True
            else:
                self.Logger.error(f"Failed to create model {new_name}")
                return False
                
        except Exception as e:
            self.Logger.error(f"Error creating model {new_name}: {e}")
            raise
    
    def LogModelCreation(self, model_name: str, parent_model: str, parameters: Dict[str, Any]) -> None:
        """Log model creation to history.
        
        Args:
            model_name: Name of the created model
            parent_model: Name of the parent model
            parameters: Dictionary of parameters set in the model
        """
        Timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if model_name not in self.ModelHistory:
            self.ModelHistory[model_name] = {
                "created_at": Timestamp,
                "parent_model": parent_model,
                "parameters": parameters
            }
        else:
            # Update existing entry
            self.ModelHistory[model_name]["updated_at"] = Timestamp
            self.ModelHistory[model_name]["parent_model"] = parent_model
            self.ModelHistory[model_name]["parameters"] = parameters
        
        # Save history
        self.SaveModelHistory()
    
    def LoadModelHistory(self) -> None:
        """Load model history from file."""
        HistoryFile = os.path.join(
            os.path.expanduser("~"), 
            ".ollama_editor", 
            "model_history.yaml"
        )
        
        try:
            if os.path.exists(HistoryFile):
                with open(HistoryFile, "r") as f:
                    History = yaml.safe_load(f) or {}
                self.ModelHistory = History
                self.Logger.info(f"Loaded model history with {len(History)} entries")
        except Exception as e:
            self.Logger.error(f"Error loading model history: {e}")
    
    def SaveModelHistory(self) -> None:
        """Save model history to file."""
        HistoryDir = os.path.join(os.path.expanduser("~"), ".ollama_editor")
        HistoryFile = os.path.join(HistoryDir, "model_history.yaml")
        
        try:
            os.makedirs(HistoryDir, exist_ok=True)
            
            with open(HistoryFile, "w") as f:
                yaml.dump(self.ModelHistory, f, default_flow_style=False)
            
            self.Logger.info(f"Saved model history with {len(self.ModelHistory)} entries")
        except Exception as e:
            self.Logger.error(f"Error saving model history: {e}")
    
    def GetModelHistory(self) -> Dict[str, Any]:
        """Get the model creation history.
        
        Returns:
            Dict[str, Any]: Dictionary of model history entries
        """
        return self.ModelHistory
    
    def GetModelVariants(self, base_model: str) -> List[str]:
        """Get variants of a base model.
        
        Args:
            base_model: Name of the base model
            
        Returns:
            List[str]: List of model variants
        """
        Variants = []
        
        for ModelName, Details in self.ModelHistory.items():
            if Details.get("parent_model") == base_model:
                Variants.append(ModelName)
        
        return Variants
