# File: ConfigManager.py
# Path: OllamaModelEditor/Core/ConfigManager.py
# Standard: AIDEV-PascalCase-1.0

import os
import yaml
import logging
from pathlib import Path

class ConfigManager:
    """Manages application configuration and settings."""
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "UI": {
            "Theme": "light",  # Options: "light", "dark", "system"
            "WindowSize": "1200x900",
            "DefaultFontSize": 10,
        },
        "Application": {
            "DefaultModelDir": "~/.ollama/models",
            "LogLevel": "INFO",  # Options: "DEBUG", "INFO", "WARNING", "ERROR"
            "AutoRefreshModels": True,
        },
        "AIAdvisor": {
            "DefaultModel": "llama3",  # Model to use for parameter advice
            "EnableAutoSuggestions": True,
            "ContextWindow": 4096,
        },
        "ParameterDocs": {
            "ShowCautions": True,
            "ShowExamples": True,
            "ShowPerformanceImpact": True,
        },
        "State": {
            "LastModel": "",
            "LastWindowSize": "1200x900",
        }
    }
    
    def __init__(self, config_file=None):
        """Initialize the configuration manager.
        
        Args:
            config_file: Optional path to a specific config file
        """
        self.ConfigFile = config_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "config.yaml"
        )
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.ConfigFile), exist_ok=True)
        
        # Load configuration
        self.Config = self.LoadConfig()
    
    def LoadConfig(self):
        """Load configuration from file.
        
        Returns:
            dict: The loaded configuration or default configuration if file doesn't exist
        """
        try:
            if os.path.exists(self.ConfigFile):
                with open(self.ConfigFile, 'r') as file:
                    config = yaml.safe_load(file)
                
                # Validate and merge with defaults to ensure all keys exist
                return self.MergeWithDefaults(config)
            else:
                # Create config file with defaults if it doesn't exist
                self.SaveConfig(self.DEFAULT_CONFIG)
                return dict(self.DEFAULT_CONFIG)
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            return dict(self.DEFAULT_CONFIG)
    
    def SaveConfig(self, config=None):
        """Save configuration to file.
        
        Args:
            config: Optional configuration to save, if None, saves the current configuration
        """
        try:
            config_to_save = config if config is not None else self.Config
            with open(self.ConfigFile, 'w') as file:
                yaml.dump(config_to_save, file, default_flow_style=False)
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
    
    def MergeWithDefaults(self, config):
        """Merge the provided configuration with defaults to ensure all keys exist.
        
        Args:
            config: The configuration to merge with defaults
            
        Returns:
            dict: The merged configuration
        """
        merged_config = dict(self.DEFAULT_CONFIG)
        
        # Only merge keys that exist in the default config
        for section in self.DEFAULT_CONFIG:
            if section in config and isinstance(config[section], dict):
                for key in self.DEFAULT_CONFIG[section]:
                    if key in config[section]:
                        merged_config[section][key] = config[section][key]
        
        return merged_config
    
    def GetTheme(self):
        """Get the current theme setting.
        
        Returns:
            str: The current theme ("light", "dark", or "system")
        """
        return self.Config.get("UI", {}).get("Theme", "light")
    
    def SetTheme(self, theme):
        """Set the theme setting.
        
        Args:
            theme: The theme to set ("light", "dark", or "system")
        """
        if "UI" not in self.Config:
            self.Config["UI"] = {}
        self.Config["UI"]["Theme"] = theme
    
    def GetLogLevel(self):
        """Get the log level setting.
        
        Returns:
            str: The log level ("DEBUG", "INFO", "WARNING", "ERROR")
        """
        return self.Config.get("Application", {}).get("LogLevel", "INFO")
    
    def GetParameterDocsSettings(self):
        """Get parameter documentation display settings.
        
        Returns:
            dict: Parameter documentation settings
        """
        return self.Config.get("ParameterDocs", self.DEFAULT_CONFIG["ParameterDocs"])
    
    def GetLastModel(self):
        """Get the last used model.
        
        Returns:
            str: The name of the last used model
        """
        return self.Config.get("State", {}).get("LastModel", "")
    
    def SetLastModel(self, model_name):
        """Set the last used model.
        
        Args:
            model_name: The name of the model
        """
        if "State" not in self.Config:
            self.Config["State"] = {}
        self.Config["State"]["LastModel"] = model_name
    
    def GetAIAdvisorSettings(self):
        """Get AI advisor settings.
        
        Returns:
            dict: AI advisor settings
        """
        return self.Config.get("AIAdvisor", self.DEFAULT_CONFIG["AIAdvisor"])
    
    def GetDefaultModelDir(self):
        """Get the default model directory.
        
        Returns:
            str: The path to the default model directory
        """
        model_dir = self.Config.get("Application", {}).get(
            "DefaultModelDir", 
            self.DEFAULT_CONFIG["Application"]["DefaultModelDir"]
        )
        
        # Expand user directory if needed
        if model_dir.startswith("~"):
            model_dir = os.path.expanduser(model_dir)
            
        return model_dir
