# File: ConfigManager.py
# Path: OllamaModelEditor/Core/ConfigManager.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Configuration management for the OllamaModelEditor application

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Special terms properly capitalized according to AIDEV-PascalCase standards
# AI, DB, GUI, API

class ConfigManager:
    """Manages application configuration settings and model parameters."""
    
    def __init__(self, ConfigPath: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            ConfigPath: Optional path to configuration file
        """
        self.ConfigPath = ConfigPath
        self.AppConfig = {}
        self.ModelConfigs = {}
        self.UserPreferences = {}
        
        # Set default configuration path if not provided
        if not self.ConfigPath:
            self.ConfigPath = self._GetDefaultConfigPath()
    
    def _GetDefaultConfigPath(self) -> str:
        """
        Determine the default configuration path based on the operating system.
        
        Returns:
            str: Path to the default configuration directory
        """
        # Get user's home directory
        HomeDir = Path.home()
        
        # Determine configuration directory based on platform
        if os.name == 'nt':  # Windows
            ConfigDir = HomeDir / 'AppData' / 'Local' / 'OllamaModelEditor'
        else:  # macOS and Linux
            ConfigDir = HomeDir / '.config' / 'ollamaModelEditor'
        
        # Create directory if it doesn't exist
        ConfigDir.mkdir(parents=True, exist_ok=True)
        
        return str(ConfigDir / 'config.yaml')
    
    def LoadConfig(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            bool: True if configuration loaded successfully, False otherwise
        """
        try:
            ConfigPath = Path(self.ConfigPath)
            
            # Create default configuration if file doesn't exist
            if not ConfigPath.exists():
                self._CreateDefaultConfig()
                return True
            
            # Load configuration based on file extension
            if ConfigPath.suffix.lower() == '.json':
                with open(ConfigPath, 'r') as ConfigFile:
                    ConfigData = json.load(ConfigFile)
            elif ConfigPath.suffix.lower() in ['.yaml', '.yml']:
                with open(ConfigPath, 'r') as ConfigFile:
                    ConfigData = yaml.safe_load(ConfigFile)
            else:
                print(f"Unsupported configuration file format: {ConfigPath.suffix}")
                return False
            
            # Parse configuration sections
            self.AppConfig = ConfigData.get('AppConfig', {})
            self.ModelConfigs = ConfigData.get('ModelConfigs', {})
            self.UserPreferences = ConfigData.get('UserPreferences', {})
            
            return True
            
        except Exception as Error:
            print(f"Error loading configuration: {Error}")
            # Create default configuration on error
            self._CreateDefaultConfig()
            return False
    
    def SaveConfig(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            bool: True if configuration saved successfully, False otherwise
        """
        try:
            ConfigPath = Path(self.ConfigPath)
            
            # Prepare configuration data
            ConfigData = {
                'AppConfig': self.AppConfig,
                'ModelConfigs': self.ModelConfigs,
                'UserPreferences': self.UserPreferences
            }
            
            # Create directory if it doesn't exist
            ConfigPath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration based on file extension
            if ConfigPath.suffix.lower() == '.json':
                with open(ConfigPath, 'w') as ConfigFile:
                    json.dump(ConfigData, ConfigFile, indent=2)
            elif ConfigPath.suffix.lower() in ['.yaml', '.yml']:
                with open(ConfigPath, 'w') as ConfigFile:
                    yaml.dump(ConfigData, ConfigFile, default_flow_style=False)
            else:
                print(f"Unsupported configuration file format: {ConfigPath.suffix}")
                return False
            
            return True
            
        except Exception as Error:
            print(f"Error saving configuration: {Error}")
            return False
    
    def _CreateDefaultConfig(self) -> None:
        """Create default configuration settings."""
        # Default application configuration
        self.AppConfig = {
            'Version': '1.0.0',
            'APIEndpoint': 'http://localhost:11434/api',
            'LogLevel': 'INFO',
            'MaxConcurrentRequests': 3,
            'Theme': 'system'
        }
        
        # Default model configurations
        self.ModelConfigs = {
            'DefaultParameters': {
                'Temperature': 0.7,
                'TopP': 0.9,
                'MaxTokens': 2048,
                'FrequencyPenalty': 0.0,
                'PresencePenalty': 0.0
            }
        }
        
        # Default user preferences
        self.UserPreferences = {
            'UIFontSize': 12,
            'EditorFontFamily': 'Consolas, Menlo, monospace',
            'ShowWelcomeOnStartup': True,
            'AutoSaveInterval': 300,  # seconds
            'RecentModels': []
        }
        
        # Save default configuration
        self.SaveConfig()
    
    def GetAppConfig(self, Key: Optional[str] = None, Default: Any = None) -> Any:
        """
        Get application configuration.
        
        Args:
            Key: Optional configuration key to retrieve
            Default: Default value if key not found
            
        Returns:
            Configuration value or entire configuration dictionary
        """
        if Key:
            return self.AppConfig.get(Key, Default)
        return self.AppConfig
    
    def SetAppConfig(self, Key: str, Value: Any) -> None:
        """
        Set application configuration.
        
        Args:
            Key: Configuration key to set
            Value: Configuration value
        """
        self.AppConfig[Key] = Value
    
    def GetModelConfig(self, ModelName: str) -> Dict[str, Any]:
        """
        Get configuration for a specific model.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            Dict: Model configuration
        """
        return self.ModelConfigs.get(ModelName, self.ModelConfigs.get('DefaultParameters', {}))
    
    def SetModelConfig(self, ModelName: str, Config: Dict[str, Any]) -> None:
        """
        Set configuration for a specific model.
        
        Args:
            ModelName: Name of the model
            Config: Model configuration
        """
        self.ModelConfigs[ModelName] = Config
    
    def GetUserPreference(self, Key: str, Default: Any = None) -> Any:
        """
        Get user preference.
        
        Args:
            Key: Preference key
            Default: Default value if preference not found
            
        Returns:
            User preference value
        """
        return self.UserPreferences.get(Key, Default)
    
    def SetUserPreference(self, Key: str, Value: Any) -> None:
        """
        Set user preference.
        
        Args:
            Key: Preference key
            Value: Preference value
        """
        self.UserPreferences[Key] = Value
    
    def AddRecentModel(self, ModelName: str) -> None:
        """
        Add model to recent models list.
        
        Args:
            ModelName: Name of the model
        """
        # Get current recent models list
        RecentModels = self.GetUserPreference('RecentModels', [])
        
        # Remove model if it already exists in the list
        if ModelName in RecentModels:
            RecentModels.remove(ModelName)
        
        # Add model to the beginning of the list
        RecentModels.insert(0, ModelName)
        
        # Keep only the 10 most recent models
        RecentModels = RecentModels[:10]
        
        # Update preference
        self.SetUserPreference('RecentModels', RecentModels)
    
    def ExportModelConfig(self, ModelName: str, FilePath: str) -> bool:
        """
        Export model configuration to a file.
        
        Args:
            ModelName: Name of the model
            FilePath: Path to save the configuration
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            # Get model configuration
            ModelConfig = self.GetModelConfig(ModelName)
            
            if not ModelConfig:
                print(f"No configuration found for model: {ModelName}")
                return False
            
            # Ensure export directory exists
            Path(FilePath).parent.mkdir(parents=True, exist_ok=True)
            
            # Export based on file extension
            FileExt = Path(FilePath).suffix.lower()
            
            if FileExt == '.json':
                with open(FilePath, 'w') as ExportFile:
                    json.dump(ModelConfig, ExportFile, indent=2)
            elif FileExt in ['.yaml', '.yml']:
                with open(FilePath, 'w') as ExportFile:
                    yaml.dump(ModelConfig, ExportFile, default_flow_style=False)
            else:
                print(f"Unsupported export format: {FileExt}")
                return False
            
            return True
            
        except Exception as Error:
            print(f"Error exporting model configuration: {Error}")
            return False
    
    def ImportModelConfig(self, ModelName: str, FilePath: str) -> bool:
        """
        Import model configuration from a file.
        
        Args:
            ModelName: Name of the model
            FilePath: Path to the configuration file
            
        Returns:
            bool: True if import successful, False otherwise
        """
        try:
            # Check if file exists
            ConfigFile = Path(FilePath)
            if not ConfigFile.exists():
                print(f"Configuration file not found: {FilePath}")
                return False
            
            # Import based on file extension
            FileExt = ConfigFile.suffix.lower()
            
            if FileExt == '.json':
                with open(FilePath, 'r') as ImportFile:
                    ModelConfig = json.load(ImportFile)
            elif FileExt in ['.yaml', '.yml']:
                with open(FilePath, 'r') as ImportFile:
                    ModelConfig = yaml.safe_load(ImportFile)
            else:
                print(f"Unsupported import format: {FileExt}")
                return False
            
            # Validate imported configuration
            if not self._ValidateModelConfig(ModelConfig):
                print("Invalid model configuration format")
                return False
            
            # Set model configuration
            self.SetModelConfig(ModelName, ModelConfig)
            
            # Add to recent models
            self.AddRecentModel(ModelName)
            
            return True
            
        except Exception as Error:
            print(f"Error importing model configuration: {Error}")
            return False
    
    def _ValidateModelConfig(self, Config: Dict[str, Any]) -> bool:
        """
        Validate model configuration format.
        
        Args:
            Config: Model configuration to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        # Required parameters for valid model configuration
        RequiredParams = ['Temperature', 'TopP', 'MaxTokens']
        
        # Check if all required parameters exist
        for Param in RequiredParams:
            if Param not in Config:
                print(f"Missing required parameter: {Param}")
                return False
        
        # Validate parameter types and ranges
        if not isinstance(Config.get('Temperature'), (int, float)) or not 0 <= Config.get('Temperature') <= 2:
            print("Temperature must be a number between 0 and 2")
            return False
        
        if not isinstance(Config.get('TopP'), (int, float)) or not 0 <= Config.get('TopP') <= 1:
            print("TopP must be a number between 0 and 1")
            return False
        
        if not isinstance(Config.get('MaxTokens'), int) or Config.get('MaxTokens') <= 0:
            print("MaxTokens must be a positive integer")
            return False
        
        return True