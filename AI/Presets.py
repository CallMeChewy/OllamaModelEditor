# File: Presets.py
# Path: OllamaModelEditor/AI/Presets.py
# Standard: AIDEV-PascalCase-1.0

import os
import yaml
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

class ParameterPresets:
    """Manages parameter presets for different use cases."""
    
    def __init__(self, config_manager, logger=None):
        """Initialize the parameter presets manager.
        
        Args:
            config_manager: The configuration manager instance
            logger: Optional logger instance
        """
        self.Config = config_manager
        self.Logger = logger or logging.getLogger("ParameterPresets")
        
        # Load built-in presets
        self.BuiltinPresets = self._LoadBuiltinPresets()
        
        # Load user presets
        self.UserPresets = self._LoadUserPresets()
    
    def _LoadBuiltinPresets(self) -> Dict[str, Dict[str, Any]]:
        """Load built-in parameter presets.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of built-in presets
        """
        return {
            "creative_writing": {
                "name": "Creative Writing",
                "description": "Optimized for creative content generation like stories and poetry",
                "parameters": {
                    "temperature": 0.9,
                    "top_p": 0.95,
                    "top_k": 60,
                    "repeat_penalty": 1.2,
                    "presence_penalty": 0.1,
                    "frequency_penalty": 0.1
                }
            },
            "code_generation": {
                "name": "Code Generation",
                "description": "Optimized for generating code with precision and consistency",
                "parameters": {
                    "temperature": 0.2,
                    "top_p": 0.7,
                    "top_k": 40,
                    "repeat_penalty": 1.05,
                    "presence_penalty": 0.0,
                    "frequency_penalty": 0.0
                }
            },
            "factual_qa": {
                "name": "Factual Q&A",
                "description": "Optimized for accurate factual responses",
                "parameters": {
                    "temperature": 0.2,
                    "top_p": 0.6,
                    "top_k": 20,
                    "repeat_penalty": 1.1,
                    "presence_penalty": 0.0,
                    "frequency_penalty": 0.0
                }
            },
            "conversation": {
                "name": "Conversation",
                "description": "Balanced settings for natural conversation",
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "presence_penalty": 0.0,
                    "frequency_penalty": 0.0
                }
            },
            "balanced": {
                "name": "Balanced",
                "description": "General-purpose settings with good balance",
                "parameters": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "presence_penalty": 0.0,
                    "frequency_penalty": 0.0
                }
            },
            "low_resource": {
                "name": "Low Resource Mode",
                "description": "Settings for running on systems with limited resources",
                "parameters": {
                    "num_ctx": 2048,
                    "num_batch": 4,
                    "num_gpu": 1,
                    "num_thread": 4
                }
            },
            "high_performance": {
                "name": "High Performance Mode",
                "description": "Settings for maximum performance on capable systems",
                "parameters": {
                    "num_ctx": 8192,
                    "num_batch": 32,
                    "num_gpu": 0,  # Use all available GPUs
                    "num_thread": 0  # Use all available threads
                }
            }
        }
    
    def _LoadUserPresets(self) -> Dict[str, Dict[str, Any]]:
        """Load user-defined parameter presets.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of user presets
        """
        UserPresets = {}
        
        try:
            # Determine the presets file path
            PresetsDir = os.path.join(os.path.expanduser("~"), ".ollama_editor")
            PresetsFile = os.path.join(PresetsDir, "presets.yaml")
            
            if os.path.exists(PresetsFile):
                with open(PresetsFile, 'r') as f:
                    UserPresets = yaml.safe_load(f) or {}
                    
                self.Logger.info(f"Loaded {len(UserPresets)} user presets")
            else:
                self.Logger.info("No user presets file found")
                
        except Exception as e:
            self.Logger.error(f"Error loading user presets: {e}")
        
        return UserPresets
    
    def SaveUserPresets(self) -> bool:
        """Save user presets to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            PresetsDir = os.path.join(os.path.expanduser("~"), ".ollama_editor")
            os.makedirs(PresetsDir, exist_ok=True)
            
            PresetsFile = os.path.join(PresetsDir, "presets.yaml")
            
            with open(PresetsFile, 'w') as f:
                yaml.dump(self.UserPresets, f, default_flow_style=False)
                
            self.Logger.info(f"Saved {len(self.UserPresets)} user presets")
            return True
            
        except Exception as e:
            self.Logger.error(f"Error saving user presets: {e}")
            return False
    
    def GetAllPresets(self) -> Dict[str, Dict[str, Any]]:
        """Get all available presets (built-in and user).
        
        Returns:
            Dict[str, Dict[str, Any]]: Combined dictionary of all presets
        """
        # Combine built-in and user presets (user presets override built-in)
        AllPresets = dict(self.BuiltinPresets)
        AllPresets.update(self.UserPresets)
        
        return AllPresets
    
    def GetPreset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific preset by ID.
        
        Args:
            preset_id: The preset identifier
            
        Returns:
            Optional[Dict[str, Any]]: The preset or None if not found
        """
        AllPresets = self.GetAllPresets()
        return AllPresets.get(preset_id)
    
    def AddUserPreset(self, preset_id: str, name: str, description: str, 
                    parameters: Dict[str, Any]) -> bool:
        """Add a new user preset.
        
        Args:
            preset_id: Unique identifier for the preset
            name: Display name for the preset
            description: Description of the preset
            parameters: Dictionary of parameter values
            
        Returns:
            bool: True if successful, False otherwise
        """
        if preset_id in self.BuiltinPresets:
            self.Logger.error(f"Cannot override built-in preset: {preset_id}")
            return False
        
        self.UserPresets[preset_id] = {
            "name": name,
            "description": description,
            "parameters": parameters
        }
        
        self.Logger.info(f"Added user preset: {preset_id}")
        return self.SaveUserPresets()
    
    def UpdateUserPreset(self, preset_id: str, name: str = None, 
                        description: str = None, parameters: Dict[str, Any] = None) -> bool:
        """Update an existing user preset.
        
        Args:
            preset_id: The preset identifier to update
            name: Optional new name
            description: Optional new description
            parameters: Optional new parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        if preset_id not in self.UserPresets:
            self.Logger.error(f"User preset not found: {preset_id}")
            return False
        
        if name is not None:
            self.UserPresets[preset_id]["name"] = name
            
        if description is not None:
            self.UserPresets[preset_id]["description"] = description
            
        if parameters is not None:
            self.UserPresets[preset_id]["parameters"] = parameters
        
        self.Logger.info(f"Updated user preset: {preset_id}")
        return self.SaveUserPresets()
    
    def DeleteUserPreset(self, preset_id: str) -> bool:
        """Delete a user preset.
        
        Args:
            preset_id: The preset identifier to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if preset_id not in self.UserPresets:
            self.Logger.error(f"User preset not found: {preset_id}")
            return False
        
        del self.UserPresets[preset_id]
        self.Logger.info(f"Deleted user preset: {preset_id}")
        
        return self.SaveUserPresets()
    
    def ImportPresets(self, file_path: str) -> Tuple[int, List[str]]:
        """Import presets from a file.
        
        Args:
            file_path: Path to the presets file (YAML or JSON)
            
        Returns:
            Tuple[int, List[str]]: Count of imported presets and list of preset IDs
        """
        try:
            # Determine file format
            _, Extension = os.path.splitext(file_path)
            
            if Extension.lower() == ".json":
                with open(file_path, 'r') as f:
                    ImportedPresets = json.load(f)
            else:
                # Default to YAML
                with open(file_path, 'r') as f:
                    ImportedPresets = yaml.safe_load(f)
            
            if not isinstance(ImportedPresets, dict):
                self.Logger.error(f"Invalid presets format in {file_path}")
                return 0, []
            
            # Add each imported preset
            imported_ids = []
            for preset_id, preset_data in ImportedPresets.items():
                # Skip if not proper format
                if not isinstance(preset_data, dict) or "parameters" not in preset_data:
                    continue
                
                name = preset_data.get("name", preset_id)
                description = preset_data.get("description", "Imported preset")
                parameters = preset_data.get("parameters", {})
                
                self.UserPresets[preset_id] = {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
                
                imported_ids.append(preset_id)
            
            # Save updated presets
            self.SaveUserPresets()
            
            self.Logger.info(f"Imported {len(imported_ids)} presets from {file_path}")
            return len(imported_ids), imported_ids
            
        except Exception as e:
            self.Logger.error(f"Error importing presets: {e}")
            return 0, []
    
    def ExportPresets(self, file_path: str, preset_ids: List[str] = None) -> bool:
        """Export presets to a file.
        
        Args:
            file_path: Path to save presets
            preset_ids: Optional list of preset IDs to export (None for all user presets)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Determine which presets to export
            if preset_ids is None:
                ExportPresets = dict(self.UserPresets)
            else:
                ExportPresets = {
                    preset_id: preset_data
                    for preset_id, preset_data in self.GetAllPresets().items()
                    if preset_id in preset_ids
                }
            
            # Determine export format
            _, Extension = os.path.splitext(file_path)
            
            if Extension.lower() == ".json":
                with open(file_path, 'w') as f:
                    json.dump(ExportPresets, f, indent=2)
            else:
                # Default to YAML
                with open(file_path, 'w') as f:
                    yaml.dump(ExportPresets, f, default_flow_style=False)
            
            self.Logger.info(f"Exported {len(ExportPresets)} presets to {file_path}")
            return True
            
        except Exception as e:
            self.Logger.error(f"Error exporting presets: {e}")
            return False
    
    def GetPresetCategories(self) -> Dict[str, List[str]]:
        """Get preset categories and their associated preset IDs.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping categories to lists of preset IDs
        """
        # Define categories and their keywords
        Categories = {
            "Generation": ["creative", "writing", "conversation", "chat", "roleplay"],
            "Technical": ["code", "factual", "qa", "technical"],
            "Performance": ["resource", "performance", "speed", "memory", "fast"],
            "Custom": []  # All user presets go here by default
        }
        
        # Categorize presets
        CategorizedPresets = {category: [] for category in Categories}
        
        # Add built-in presets to appropriate categories
        for preset_id, preset_data in self.BuiltinPresets.items():
            assigned = False
            
            for category, keywords in Categories.items():
                if any(kw in preset_id.lower() or 
                       kw in preset_data.get("name", "").lower() or 
                       kw in preset_data.get("description", "").lower() 
                       for kw in keywords):
                    CategorizedPresets[category].append(preset_id)
                    assigned = True
                    break
            
            # Add to "Other" if not assigned
            if not assigned:
                if "Other" not in CategorizedPresets:
                    CategorizedPresets["Other"] = []
                CategorizedPresets["Other"].append(preset_id)
        
        # Add all user presets to "Custom" category
        CategorizedPresets["Custom"] = list(self.UserPresets.keys())
        
        return CategorizedPresets