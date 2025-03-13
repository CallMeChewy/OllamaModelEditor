# File: ModelManagerExtensions.py
# Path: OllamaModelEditor/Core/ModelManagerExtensions.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-13
# Last Modified: 2025-03-13
# Description: Extensions for ModelManager to support preset handling

from typing import Dict, List, Any, Optional

class ModelManagerExtensions:
    """
    This class provides extension methods for the ModelManager class.
    
    These methods should be added to the ModelManager class to extend its functionality.
    """
    
    def GetPresetParameters(self, PresetName: str) -> Dict[str, Any]:
        """
        Get parameters for a preset.
        
        Args:
            PresetName: Name of the preset
            
        Returns:
            Dict containing preset parameters or empty dict if not found
        """
        # Define built-in presets
        BuiltInPresets = {
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
            },
            "Balanced": {
                'Temperature': 0.6,
                'TopP': 0.85,
                'MaxTokens': 2048,
                'FrequencyPenalty': 0.3,
                'PresencePenalty': 0.3
            },
            "Deterministic": {
                'Temperature': 0.0,
                'TopP': 0.5,
                'MaxTokens': 2048,
                'FrequencyPenalty': 0.0,
                'PresencePenalty': 0.0
            }
        }
        
        # Check if preset is a built-in preset
        if PresetName in BuiltInPresets:
            return BuiltInPresets[PresetName]
        
        # If using database, try to get from database
        if self.DB:
            # Try to get from database
            Preset = self.DB.GetPreset(PresetName)
            if Preset:
                return {
                    'Temperature': Preset['Temperature'],
                    'TopP': Preset['TopP'],
                    'MaxTokens': Preset['MaxTokens'],
                    'FrequencyPenalty': Preset['FrequencyPenalty'],
                    'PresencePenalty': Preset['PresencePenalty']
                }
            
            # Try to get from user presets
            UserPreset = self.DB.ExecuteQuery(
                "SELECT * FROM UserPresets WHERE Name = ?",
                (PresetName,)
            )
            if UserPreset:
                return {
                    'Temperature': UserPreset[0][3],  # Index based on UserPresets schema
                    'TopP': UserPreset[0][4],
                    'MaxTokens': UserPreset[0][5],
                    'FrequencyPenalty': UserPreset[0][6],
                    'PresencePenalty': UserPreset[0][7]
                }
        
        # Return default parameters if preset not found
        return self.Config.GetModelConfig('DefaultParameters')
    
    def GetAllPresets(self) -> List[Dict[str, Any]]:
        """
        Get all available presets.
        
        Returns:
            List of dictionaries containing preset information
        """
        Presets = []
        
        # Add built-in presets
        BuiltInPresets = [
            {
                'Name': 'Default',
                'Description': 'Balanced settings suitable for most tasks.',
                'IsBuiltIn': True
            },
            {
                'Name': 'Creative',
                'Description': 'Higher temperature and diversity for more creative, varied outputs.',
                'IsBuiltIn': True
            },
            {
                'Name': 'Precise',
                'Description': 'Lower temperature for more focused, deterministic responses.',
                'IsBuiltIn': True
            },
            {
                'Name': 'Fast',
                'Description': 'Optimized for speed with shorter outputs.',
                'IsBuiltIn': True
            },
            {
                'Name': 'Balanced',
                'Description': 'Moderate settings with some repetition control for well-rounded responses.',
                'IsBuiltIn': True
            },
            {
                'Name': 'Deterministic',
                'Description': 'Minimal randomness for highly predictable, consistent outputs.',
                'IsBuiltIn': True
            }
        ]
        
        Presets.extend(BuiltInPresets)
        
        # If using database, add presets from database
        if self.DB:
            # Get presets from database
            DBPresets = self.DB.GetPresets()
            for Preset in DBPresets:
                # Skip presets that match built-in names
                if any(BP['Name'] == Preset.get('Name', '') for BP in BuiltInPresets):
                    continue
                
                Presets.append({
                    'Name': Preset.get('Name', 'Unknown'),
                    'Description': Preset.get('Description', ''),
                    'IsBuiltIn': False
                })
            
            # Get user presets from database
            UserPresets = self.DB.GetUserPresets()
            for Preset in UserPresets:
                Presets.append({
                    'Name': Preset.get('Name', 'Unknown'),
                    'Description': Preset.get('Description', ''),
                    'IsBuiltIn': False,
                    'IsUserPreset': True
                })
        
        return Presets
    
    def ApplyPresetToModel(self, ModelName: str, PresetName: str) -> bool:
        """
        Apply a preset to a model.
        
        Args:
            ModelName: Name of the model
            PresetName: Name of the preset
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get preset parameters
        PresetParams = self.GetPresetParameters(PresetName)
        
        if not PresetParams:
            self.Logger.error(f"Preset not found: {PresetName}")
            return False
        
        # Update model parameters
        Success = self.UpdateModelParameters(ModelName, PresetParams)
        
        if Success:
            self.Logger.info(f"Applied preset '{PresetName}' to model '{ModelName}'")
        
        return Success
    
    def SaveUserPreset(self, PresetName: str, Description: str, Parameters: Dict[str, Any]) -> bool:
        """
        Save a user preset.
        
        Args:
            PresetName: Name of the preset
            Description: Description of the preset
            Parameters: Parameter values for the preset
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate parameters
        if not self._ValidateParameters(Parameters):
            self.Logger.error("Invalid parameters for preset")
            return False
        
        # Save to database if available
        if self.DB:
            try:
                self.DB.SaveUserPreset(PresetName, Description, Parameters)
                self.Logger.info(f"User preset '{PresetName}' saved")
                return True
            except Exception as Error:
                self.Logger.error(f"Error saving user preset: {Error}")
                return False
        else:
            self.Logger.error("Database not available, cannot save user preset")
            return False
    
    def DeleteUserPreset(self, PresetName: str) -> bool:
        """
        Delete a user preset.
        
        Args:
            PresetName: Name of the preset
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Delete from database if available
        if self.DB:
            try:
                Result = self.DB.DeleteUserPreset(PresetName)
                if Result:
                    self.Logger.info(f"User preset '{PresetName}' deleted")
                else:
                    self.Logger.warning(f"User preset '{PresetName}' not found")
                return Result
            except Exception as Error:
                self.Logger.error(f"Error deleting user preset: {Error}")
                return False
        else:
            self.Logger.error("Database not available, cannot delete user preset")
            return False

# Extension function to integrate these methods into ModelManager
def ExtendModelManager(ModelManager):
    """
    Extend ModelManager with preset handling methods.
    
    Args:
        ModelManager: The ModelManager class to extend
    """
    # Add methods from ModelManagerExtensions to ModelManager
    ModelManager.GetPresetParameters = ModelManagerExtensions.GetPresetParameters
    ModelManager.GetAllPresets = ModelManagerExtensions.GetAllPresets
    ModelManager.ApplyPresetToModel = ModelManagerExtensions.ApplyPresetToModel
    ModelManager.SaveUserPreset = ModelManagerExtensions.SaveUserPreset
    ModelManager.DeleteUserPreset = ModelManagerExtensions.DeleteUserPreset
