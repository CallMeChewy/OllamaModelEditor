# File: ConfigManager.py
# Path: OllamaModelEditor/Core/ConfigManager.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-13
# Description: Configuration management for the OllamaModelEditor application

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import logging

# Import DBManager if available
try:
    from Core.DBManager import DBManager
except ImportError:
    DBManager = None

class ConfigManager:
    """Manages application configuration settings and model parameters."""
    
    def __init__(self, ConfigPath: Optional[str] = None, DB: Optional['DBManager'] = None):
        """
        Initialize the configuration manager.
        
        Args:
            ConfigPath: Optional path to configuration file
            DB: Optional database manager instance
        """
        self.Logger = logging.getLogger('OllamaModelEditor.ConfigManager')
        self.ConfigPath = ConfigPath
        self.DB = DB
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
            ConfigDir = HomeDir / '.config' / 'OllamaModelEditor'
        
        # Create directory if it doesn't exist
        ConfigDir.mkdir(parents=True, exist_ok=True)
        
        return str(ConfigDir / 'Config.yaml')
    
    def _SerializeQtObjects(self, Config: Dict) -> Dict:
        """
        Convert Qt objects to serializable format.
        
        Args:
            Config: Configuration dictionary
            
        Returns:
            Dictionary with serialized Qt objects
        """
        SerializedConfig = {}
        
        for Key, Value in Config.items():
            if hasattr(Value, '__class__') and Value.__class__.__module__.startswith('PySide6'):
                # Handle QByteArray
                if Value.__class__.__name__ == 'QByteArray':
                    SerializedConfig[Key] = {'__qt_type__': 'QByteArray', 'data': bytes(Value).hex()}
                # Handle QSize
                elif Value.__class__.__name__ == 'QSize':
                    SerializedConfig[Key] = {'__qt_type__': 'QSize', 'width': Value.width(), 'height': Value.height()}
                # Handle QRect
                elif Value.__class__.__name__ == 'QRect':
                    SerializedConfig[Key] = {
                        '__qt_type__': 'QRect', 
                        'x': Value.x(), 
                        'y': Value.y(),
                        'width': Value.width(), 
                        'height': Value.height()
                    }
                # Handle QPoint
                elif Value.__class__.__name__ == 'QPoint':
                    SerializedConfig[Key] = {'__qt_type__': 'QPoint', 'x': Value.x(), 'y': Value.y()}
                # Other Qt objects - store class name and basic representation
                else:
                    SerializedConfig[Key] = {
                        '__qt_type__': Value.__class__.__name__,
                        'repr': repr(Value)
                    }
            elif isinstance(Value, dict):
                SerializedConfig[Key] = self._SerializeQtObjects(Value)
            else:
                SerializedConfig[Key] = Value
                
        return SerializedConfig
    
    def _DeserializeQtObjects(self, Config: Dict) -> Dict:
        """
        Convert serialized Qt objects back to their original form.
        
        Args:
            Config: Configuration dictionary with serialized Qt objects
            
        Returns:
            Dictionary with deserialized Qt objects
        """
        from PySide6.QtCore import QByteArray, QSize, QRect, QPoint
        
        DeserializedConfig = {}
        
        for Key, Value in Config.items():
            if isinstance(Value, dict) and '__qt_type__' in Value:
                # Reconstruct Qt objects based on type
                QtType = Value['__qt_type__']
                
                if QtType == 'QByteArray':
                    DeserializedConfig[Key] = QByteArray.fromHex(bytes.fromhex(Value['data']))
                elif QtType == 'QSize':
                    DeserializedConfig[Key] = QSize(Value['width'], Value['height'])
                elif QtType == 'QRect':
                    DeserializedConfig[Key] = QRect(Value['x'], Value['y'], Value['width'], Value['height'])
                elif QtType == 'QPoint':
                    DeserializedConfig[Key] = QPoint(Value['x'], Value['y'])
                else:
                    # For other Qt objects, we can't fully reconstruct them
                    # So we'll keep them as dictionaries with their type information
                    DeserializedConfig[Key] = Value
            elif isinstance(Value, dict):
                DeserializedConfig[Key] = self._DeserializeQtObjects(Value)
            else:
                DeserializedConfig[Key] = Value
                
        return DeserializedConfig
    
    def LoadConfig(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            bool: True if configuration loaded successfully, False otherwise
        """
        # If using database, populate from there
        if self.DB:
            try:
                # Load app config from database
                self._LoadAppConfigFromDB()
                
                # Load user preferences from database
                self._LoadUserPreferencesFromDB()
                
                # Load model configs from database
                self._LoadModelConfigsFromDB()
                
                self.Logger.info("Configuration loaded from database")
                return True
            
            except Exception as Error:
                self.Logger.error(f"Error loading configuration from database: {Error}")
                # Fall back to file-based configuration
        
        # File-based configuration loading
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
                self.Logger.error(f"Unsupported configuration file format: {ConfigPath.suffix}")
                return False
            
            # Parse configuration sections
            if 'AppConfig' in ConfigData:
                self.AppConfig = self._DeserializeQtObjects(ConfigData.get('AppConfig', {}))
            
            if 'ModelConfigs' in ConfigData:
                self.ModelConfigs = self._DeserializeQtObjects(ConfigData.get('ModelConfigs', {}))
            
            if 'UserPreferences' in ConfigData:
                self.UserPreferences = self._DeserializeQtObjects(ConfigData.get('UserPreferences', {}))
            
            self.Logger.info(f"Configuration loaded from file: {ConfigPath}")
            return True
            
        except Exception as Error:
            self.Logger.error(f"Error loading configuration: {Error}")
            # Create default configuration on error
            self._CreateDefaultConfig()
            return False
    
    def _LoadAppConfigFromDB(self) -> None:
        """Load application configuration from database."""
        # Get all app settings
        Settings = self.DB.ExecuteQuery(
            "SELECT Key, Value, ValueType FROM AppSettings"
        )
        
        # Clear existing app config
        self.AppConfig = {}
        
        # Convert settings to appropriate types and add to AppConfig
        for Key, Value, ValueType in Settings:
            if ValueType == "int":
                self.AppConfig[Key] = int(Value)
            elif ValueType == "float":
                self.AppConfig[Key] = float(Value)
            elif ValueType == "bool":
                self.AppConfig[Key] = Value.lower() in ("true", "1", "yes")
            elif ValueType == "json":
                self.AppConfig[Key] = json.loads(Value)
            else:
                self.AppConfig[Key] = Value
    
    def _LoadUserPreferencesFromDB(self) -> None:
        """Load user preferences from database."""
        # Get all user preferences
        Preferences = self.DB.ExecuteQuery(
            "SELECT Key, Value, ValueType FROM UserPreferences"
        )
        
        # Clear existing preferences
        self.UserPreferences = {}
        
        # Convert preferences to appropriate types and add to UserPreferences
        for Key, Value, ValueType in Preferences:
            if ValueType == "int":
                self.UserPreferences[Key] = int(Value)
            elif ValueType == "float":
                self.UserPreferences[Key] = float(Value)
            elif ValueType == "bool":
                self.UserPreferences[Key] = Value.lower() in ("true", "1", "yes")
            elif ValueType == "json":
                self.UserPreferences[Key] = json.loads(Value)
            else:
                self.UserPreferences[Key] = Value
    
    def _LoadModelConfigsFromDB(self) -> None:
        """Load model configurations from database."""
        # Get all model configurations
        ModelConfigs = self.DB.ExecuteQuery(
            """
            SELECT ModelName, ConfigName, Temperature, TopP, MaxTokens,
                   FrequencyPenalty, PresencePenalty
            FROM ModelConfigs
            """
        )
        
        # Clear existing model configs
        self.ModelConfigs = {}
        
        # Group configurations by model
        for ModelName, ConfigName, Temperature, TopP, MaxTokens, FrequencyPenalty, PresencePenalty in ModelConfigs:
            # Create model entry if it doesn't exist
            if ModelName not in self.ModelConfigs:
                self.ModelConfigs[ModelName] = {}
            
            # Add configuration
            self.ModelConfigs[ModelName][ConfigName] = {
                'Temperature': Temperature,
                'TopP': TopP,
                'MaxTokens': MaxTokens,
                'FrequencyPenalty': FrequencyPenalty,
                'PresencePenalty': PresencePenalty
            }
    
    def SaveConfig(self) -> bool:
        """
        Save current configuration to file or database.
        
        Returns:
            bool: True if configuration saved successfully, False otherwise
        """
        # If using database, save there
        if self.DB:
            try:
                # Save app config to database
                for Key, Value in self.AppConfig.items():
                    self.DB.SetAppSetting(Key, Value)
                
                # Save user preferences to database
                for Key, Value in self.UserPreferences.items():
                    self.DB.SetUserPreference(Key, Value)
                
                # Save model configs to database (handled by ModelManager)
                # We don't save model configs here to avoid overwriting changes
                
                self.Logger.info("Configuration saved to database")
                return True
            
            except Exception as Error:
                self.Logger.error(f"Error saving configuration to database: {Error}")
                # Fall back to file-based saving
        
        # File-based configuration saving
        try:
            ConfigPath = Path(self.ConfigPath)
            
            # Prepare configuration data
            ConfigData = {
                'AppConfig': self._SerializeQtObjects(self.AppConfig),
                'ModelConfigs': self._SerializeQtObjects(self.ModelConfigs),
                'UserPreferences': self._SerializeQtObjects(self.UserPreferences)
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
                self.Logger.error(f"Unsupported configuration file format: {ConfigPath.suffix}")
                return False
            
            self.Logger.info(f"Configuration saved to file: {ConfigPath}")
            return True
            
        except Exception as Error:
            self.Logger.error(f"Error saving configuration: {Error}")
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
        if self.DB:
            # Save to database
            for Key, Value in self.AppConfig.items():
                self.DB.SetAppSetting(Key, Value)
            
            for Key, Value in self.UserPreferences.items():
                self.DB.SetUserPreference(Key, Value)
            
            # Save default parameters
            DefaultParams = self.ModelConfigs['DefaultParameters']
            self.DB.SaveModelConfig('DefaultParameters', 'Default', DefaultParams)
            
            self.Logger.info("Default configuration created and saved to database")
        else:
            # Save to file
            self.SaveConfig()
            self.Logger.info("Default configuration created and saved to file")
    
    def GetAppConfig(self, Key: Optional[str] = None, Default: Any = None) -> Any:
        """
        Get application configuration.
        
        Args:
            Key: Optional configuration key to retrieve
            Default: Default value if key not found
            
        Returns:
            Configuration value or entire configuration dictionary
        """
        if self.DB and Key:
            # Try to get from database first
            Value = self.DB.GetAppSetting(Key, None)
            if Value is not None:
                return Value
        
        # Fall back to memory cache
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
        
        # Save to database if available
        if self.DB:
            self.DB.SetAppSetting(Key, Value)
    
    def GetModelConfig(self, ModelName: str) -> Dict[str, Any]:
        """
        Get configuration for a specific model.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            Dict: Model configuration
        """
        if self.DB:
            # Try to get from database first
            Config = self.DB.GetModelConfig(ModelName)
            if Config:
                return {
                    'Temperature': Config['Temperature'],
                    'TopP': Config['TopP'],
                    'MaxTokens': Config['MaxTokens'],
                    'FrequencyPenalty': Config['FrequencyPenalty'],
                    'PresencePenalty': Config['PresencePenalty']
                }
        
        # Fall back to memory cache
        return self.ModelConfigs.get(ModelName, self.ModelConfigs.get('DefaultParameters', {}))
    
    def SetModelConfig(self, ModelName: str, Config: Dict[str, Any]) -> None:
        """
        Set configuration for a specific model.
        
        Args:
            ModelName: Name of the model
            Config: Model configuration
        """
        self.ModelConfigs[ModelName] = Config
        
        # Save to database if available
        if self.DB:
            self.DB.SaveModelConfig(ModelName, 'Default', Config)
    
    def GetUserPreference(self, Key: str, Default: Any = None) -> Any:
        """
        Get user preference.
        
        Args:
            Key: Preference key
            Default: Default value if preference not found
            
        Returns:
            User preference value
        """
        if self.DB:
            # Try to get from database first
            Value = self.DB.GetUserPreference(Key, None)
            if Value is not None:
                return Value
        
        # Fall back to memory cache
        return self.UserPreferences.get(Key, Default)
    
    def SetUserPreference(self, Key: str, Value: Any) -> None:
        """
        Set user preference.
        
        Args:
            Key: Preference key
            Value: Preference value
        """
        self.UserPreferences[Key] = Value
        
        # Save to database if available
        if self.DB:
            self.DB.SetUserPreference(Key, Value)
    
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
                self.Logger.error(f"No configuration found for model: {ModelName}")
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
                self.Logger.error(f"Unsupported export format: {FileExt}")
                return False
            
            self.Logger.info(f"Model configuration exported to: {FilePath}")
            return True
            
        except Exception as Error:
            self.Logger.error(f"Error exporting model configuration: {Error}")
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
                self.Logger.error(f"Configuration file not found: {FilePath}")
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
                self.Logger.error(f"Unsupported import format: {FileExt}")
                return False
            
            # Validate imported configuration
            if not self._ValidateModelConfig(ModelConfig):
                self.Logger.error("Invalid model configuration format")
                return False
            
            # Set model configuration
            self.SetModelConfig(ModelName, ModelConfig)
            
            # Add to recent models
            self.AddRecentModel(ModelName)
            
            self.Logger.info(f"Model configuration imported from: {FilePath}")
            return True
            
        except Exception as Error:
            self.Logger.error(f"Error importing model configuration: {Error}")
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
                self.Logger.error(f"Missing required parameter: {Param}")
                return False
        
        # Validate parameter types and ranges
        if not isinstance(Config.get('Temperature'), (int, float)) or not 0 <= Config.get('Temperature') <= 2:
            self.Logger.error("Temperature must be a number between 0 and 2")
            return False
        
        if not isinstance(Config.get('TopP'), (int, float)) or not 0 <= Config.get('TopP') <= 1:
            self.Logger.error("TopP must be a number between 0 and 1")
            return False
        
        if not isinstance(Config.get('MaxTokens'), int) or Config.get('MaxTokens') <= 0:
            self.Logger.error("MaxTokens must be a positive integer")
            return False
        
        return True
    
    def MigrateToDatabase(self, DB: 'DBManager') -> bool:
        """
        Migrate file-based configuration to database.
        
        Args:
            DB: Database manager instance
            
        Returns:
            bool: True if migration successful, False otherwise
        """
        if not DB:
            self.Logger.error("No database manager provided")
            return False
        
        try:
            # Make sure configuration is loaded
            self.LoadConfig()
            
            # Set database reference
            self.DB = DB
            
            # Migrate application settings
            self.Logger.info("Migrating application settings...")
            for Key, Value in self.AppConfig.items():
                DB.SetAppSetting(Key, Value)
            
            # Migrate user preferences
            self.Logger.info("Migrating user preferences...")
            for Key, Value in self.UserPreferences.items():
                DB.SetUserPreference(Key, Value)
            
            # Migrate model configurations
            self.Logger.info("Migrating model configurations...")
            for ModelName, ModelConfig in self.ModelConfigs.items():
                if isinstance(ModelConfig, dict) and not isinstance(list(ModelConfig.values())[0], dict):
                    # This is a single configuration (not a dict of configs)
                    DB.SaveModelConfig(ModelName, "Default", ModelConfig)
                else:
                    # This is a dict of configurations
                    for ConfigName, ConfigParams in ModelConfig.items():
                        DB.SaveModelConfig(ModelName, ConfigName, ConfigParams)
            
            self.Logger.info("Migration to database completed successfully")
            return True
            
        except Exception as Error:
            self.Logger.error(f"Error migrating to database: {Error}")
            return False
