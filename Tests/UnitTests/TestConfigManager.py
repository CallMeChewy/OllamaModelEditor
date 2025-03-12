# File: TestConfigManager.py
# Path: OllamaModelEditor/Tests/UnitTests/TestConfigManager.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Unit tests for the ConfigManager module

import os
import sys
import json
import yaml
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any

# Add project root to path for imports
ProjectRoot = Path(__file__).resolve().parents[2]
sys.path.append(str(ProjectRoot))

# Import the module to test
from Core.ConfigManager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Test case for the ConfigManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.TempDir = tempfile.TemporaryDirectory()
        self.ConfigPath = os.path.join(self.TempDir.name, "test_config.yaml")
        
        # Create a ConfigManager instance with the test path
        self.ConfigManager = ConfigManager(self.ConfigPath)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.TempDir.cleanup()
    
    def test_InitialState(self):
        """Test initial state of ConfigManager."""
        # Check that ConfigPath is set correctly
        self.assertEqual(self.ConfigManager.ConfigPath, self.ConfigPath)
        
        # Check that initial dictionaries are empty
        self.assertEqual(self.ConfigManager.AppConfig, {})
        self.assertEqual(self.ConfigManager.ModelConfigs, {})
        self.assertEqual(self.ConfigManager.UserPreferences, {})
    
    def test_CreateDefaultConfig(self):
        """Test creation of default configuration."""
        # Call method to create default configuration
        self.ConfigManager._CreateDefaultConfig()
        
        # Check that AppConfig contains expected default values
        self.assertIn('Version', self.ConfigManager.AppConfig)
        self.assertIn('APIEndpoint', self.ConfigManager.AppConfig)
        self.assertIn('LogLevel', self.ConfigManager.AppConfig)
        
        # Check that ModelConfigs contains DefaultParameters
        self.assertIn('DefaultParameters', self.ConfigManager.ModelConfigs)
        
        # Check that UserPreferences contains expected default values
        self.assertIn('UIFontSize', self.ConfigManager.UserPreferences)
        self.assertIn('EditorFontFamily', self.ConfigManager.UserPreferences)
    
    def test_SaveAndLoadConfig(self):
        """Test saving and loading configuration."""
        # Set test values
        TestAppConfig = {
            'Version': '1.0.0-test',
            'APIEndpoint': 'http://test-endpoint:11434',
            'LogLevel': 'DEBUG'
        }
        
        TestModelConfigs = {
            'DefaultParameters': {
                'Temperature': 0.5,
                'TopP': 0.8,
                'MaxTokens': 1000
            },
            'TestModel': {
                'Temperature': 0.7,
                'TopP': 0.9,
                'MaxTokens': 2000
            }
        }
        
        TestUserPreferences = {
            'UIFontSize': 14,
            'EditorFontFamily': 'Test Font',
            'ShowWelcomeOnStartup': False
        }
        
        # Set values in ConfigManager
        self.ConfigManager.AppConfig = TestAppConfig
        self.ConfigManager.ModelConfigs = TestModelConfigs
        self.ConfigManager.UserPreferences = TestUserPreferences
        
        # Save configuration
        SaveResult = self.ConfigManager.SaveConfig()
        self.assertTrue(SaveResult, "SaveConfig should return True")
        
        # Check that file was created
        self.assertTrue(os.path.exists(self.ConfigPath), "Config file should exist")
        
        # Create a new ConfigManager instance to load the saved configuration
        NewConfigManager = ConfigManager(self.ConfigPath)
        
        # Load configuration
        LoadResult = NewConfigManager.LoadConfig()
        self.assertTrue(LoadResult, "LoadConfig should return True")
        
        # Check that loaded values match original values
        self.assertEqual(NewConfigManager.AppConfig, TestAppConfig)
        self.assertEqual(NewConfigManager.ModelConfigs, TestModelConfigs)
        self.assertEqual(NewConfigManager.UserPreferences, TestUserPreferences)
    
    def test_GetSetAppConfig(self):
        """Test get and set methods for AppConfig."""
        # Set test values
        self.ConfigManager.SetAppConfig('TestKey', 'TestValue')
        self.ConfigManager.SetAppConfig('AnotherKey', 123)
        
        # Get values
        TestValue = self.ConfigManager.GetAppConfig('TestKey')
        AnotherValue = self.ConfigManager.GetAppConfig('AnotherKey')
        
        # Check values
        self.assertEqual(TestValue, 'TestValue')
        self.assertEqual(AnotherValue, 123)
        
        # Get default value for non-existent key
        NonExistentValue = self.ConfigManager.GetAppConfig('NonExistentKey', 'DefaultValue')
        self.assertEqual(NonExistentValue, 'DefaultValue')
        
        # Get entire AppConfig
        EntireConfig = self.ConfigManager.GetAppConfig()
        self.assertEqual(EntireConfig, {
            'TestKey': 'TestValue',
            'AnotherKey': 123
        })
    
    def test_GetSetModelConfig(self):
        """Test get and set methods for ModelConfigs."""
        # Define test model configuration
        TestModelConfig = {
            'Temperature': 0.8,
            'TopP': 0.95,
            'MaxTokens': 1500
        }
        
        # Set model configuration
        self.ConfigManager.SetModelConfig('TestModel', TestModelConfig)
        
        # Get model configuration
        ModelConfig = self.ConfigManager.GetModelConfig('TestModel')
        
        # Check that retrieved configuration matches
        self.assertEqual(ModelConfig, TestModelConfig)
        
        # Get configuration for non-existent model (should return DefaultParameters)
        # First set DefaultParameters
        DefaultConfig = {
            'Temperature': 0.7,
            'TopP': 0.9,
            'MaxTokens': 2000
        }
        self.ConfigManager.SetModelConfig('DefaultParameters', DefaultConfig)
        
        # Get non-existent model
        NonExistentModel = self.ConfigManager.GetModelConfig('NonExistentModel')
        
        # Should return DefaultParameters
        self.assertEqual(NonExistentModel, DefaultConfig)
    
    def test_GetSetUserPreference(self):
        """Test get and set methods for UserPreferences."""
        # Set test values
        self.ConfigManager.SetUserPreference('TestPref', 'TestValue')
        self.ConfigManager.SetUserPreference('AnotherPref', 456)
        
        # Get values
        TestValue = self.ConfigManager.GetUserPreference('TestPref')
        AnotherValue = self.ConfigManager.GetUserPreference('AnotherPref')
        
        # Check values
        self.assertEqual(TestValue, 'TestValue')
        self.assertEqual(AnotherValue, 456)
        
        # Get default value for non-existent key
        NonExistentValue = self.ConfigManager.GetUserPreference('NonExistentPref', 'DefaultValue')
        self.assertEqual(NonExistentValue, 'DefaultValue')
    
    def test_AddRecentModel(self):
        """Test adding models to recent models list."""
        # Initially recent models should be empty
        RecentModels = self.ConfigManager.GetUserPreference('RecentModels', [])
        self.assertEqual(RecentModels, [])
        
        # Add a model
        self.ConfigManager.AddRecentModel('Model1')
        RecentModels = self.ConfigManager.GetUserPreference('RecentModels', [])
        self.assertEqual(RecentModels, ['Model1'])
        
        # Add another model
        self.ConfigManager.AddRecentModel('Model2')
        RecentModels = self.ConfigManager.GetUserPreference('RecentModels', [])
        self.assertEqual(RecentModels, ['Model2', 'Model1'])
        
        # Add the first model again (should move to front)
        self.ConfigManager.AddRecentModel('Model1')
        RecentModels = self.ConfigManager.GetUserPreference('RecentModels', [])
        self.assertEqual(RecentModels, ['Model1', 'Model2'])
        
        # Add models until we exceed the limit of 10
        for i in range(3, 12):
            self.ConfigManager.AddRecentModel(f'Model{i}')
        
        # Check that we only have 10 models and the oldest is removed
        RecentModels = self.ConfigManager.GetUserPreference('RecentModels', [])
        self.assertEqual(len(RecentModels), 10)
        self.assertEqual(RecentModels[0], 'Model11')
        self.assertNotIn('Model2', RecentModels)
    
    def test_ExportModelConfig(self):
        """Test exporting model configuration to a file."""
        # Define test model configuration
        TestModelConfig = {
            'Temperature': 0.8,
            'TopP': 0.95,
            'MaxTokens': 1500
        }
        
        # Set model configuration
        self.ConfigManager.SetModelConfig('TestModel', TestModelConfig)
        
        # Export to JSON
        JsonPath = os.path.join(self.TempDir.name, "test_export.json")
        JsonResult = self.ConfigManager.ExportModelConfig('TestModel', JsonPath)
        self.assertTrue(JsonResult, "ExportModelConfig should return True for JSON")
        self.assertTrue(os.path.exists(JsonPath), "JSON export file should exist")
        
        # Read exported JSON and verify
        with open(JsonPath, 'r') as JsonFile:
            ExportedJson = json.load(JsonFile)
        self.assertEqual(ExportedJson, TestModelConfig)
        
        # Export to YAML
        YamlPath = os.path.join(self.TempDir.name, "test_export.yaml")
        YamlResult = self.ConfigManager.ExportModelConfig('TestModel', YamlPath)
        self.assertTrue(YamlResult, "ExportModelConfig should return True for YAML")
        self.assertTrue(os.path.exists(YamlPath), "YAML export file should exist")
        
        # Read exported YAML and verify
        with open(YamlPath, 'r') as YamlFile:
            ExportedYaml = yaml.safe_load(YamlFile)
        self.assertEqual(ExportedYaml, TestModelConfig)
        
        # Test export for non-existent model
        NonExistentResult = self.ConfigManager.ExportModelConfig('NonExistentModel', JsonPath)
        self.assertFalse(NonExistentResult, "ExportModelConfig should return False for non-existent model")
        
        # Test export with unsupported format
        BadFormatPath = os.path.join(self.TempDir.name, "test_export.txt")
        BadFormatResult = self.ConfigManager.ExportModelConfig('TestModel', BadFormatPath)
        self.assertFalse(BadFormatResult, "ExportModelConfig should return False for unsupported format")
    
    def test_ValidateModelConfig(self):
        """Test validation of model configuration."""
        # Valid configuration
        ValidConfig = {
            'Temperature': 0.8,
            'TopP': 0.9,
            'MaxTokens': 2000
        }
        self.assertTrue(self.ConfigManager._ValidateModelConfig(ValidConfig))
        
        # Missing required parameter
        MissingParam = {
            'Temperature': 0.8,
            'TopP': 0.9
            # Missing MaxTokens
        }
        self.assertFalse(self.ConfigManager._ValidateModelConfig(MissingParam))
        
        # Invalid Temperature (too high)
        InvalidTemp = {
            'Temperature': 3.0,  # Should be between 0 and 2
            'TopP': 0.9,
            'MaxTokens': 2000
        }
        self.assertFalse(self.ConfigManager._ValidateModelConfig(InvalidTemp))
        
        # Invalid TopP (too high)
        InvalidTopP = {
            'Temperature': 0.8,
            'TopP': 1.5,  # Should be between 0 and 1
            'MaxTokens': 2000
        }
        self.assertFalse(self.ConfigManager._ValidateModelConfig(InvalidTopP))
        
        # Invalid MaxTokens (negative)
        InvalidTokens = {
            'Temperature': 0.8,
            'TopP': 0.9,
            'MaxTokens': -100  # Should be positive
        }
        self.assertFalse(self.ConfigManager._ValidateModelConfig(InvalidTokens))

if __name__ == '__main__':
    unittest.main()
