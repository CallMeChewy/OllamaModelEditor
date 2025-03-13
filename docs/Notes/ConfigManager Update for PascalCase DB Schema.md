# ConfigManager Update for PascalCase Database Schema

## Overview

The `ConfigManager` class needs to be updated to work with the new PascalCase database schema. This document outlines the necessary changes and provides a plan for implementation.

## Required Changes

1. Update database interaction methods to use PascalCase column names
2. Update method names to consistently use PascalCase (if any are not already)
3. Ensure all variable names follow PascalCase conventions
4. Update any hardcoded SQL queries to use the new column names
5. Modify database-related methods to work with the new schema

## Implementation Plan

### 1. Update DB-Related Methods

The following methods in the `ConfigManager` class need to be updated:

- `_LoadAppConfigFromDB()`
- `_LoadUserPreferencesFromDB()`
- `_LoadModelConfigsFromDB()`
- `MigrateToDatabase()`

### 2. Update SQL Queries

All SQL queries in the class need to be updated to use PascalCase column names. For example:

Old:
```python
Settings = self.DB.ExecuteQuery(
    "SELECT key, value, value_type FROM AppSettings"
)
```

New:
```python
Settings = self.DB.ExecuteQuery(
    "SELECT Key, Value, ValueType FROM AppSettings"
)
```

### 3. Update Database Path Logic

Ensure the database path logic uses PascalCase for filenames:

Old:
```python
return str(ConfigDir / 'ollama_model_editor.db')
```

New:
```python
return str(ConfigDir / 'OllamaModelEditor.db')
```

### 4. Update Dictionary Keys

Update dictionary keys to maintain PascalCase throughout:

Old:
```python
self.AppConfig[Key] = Value
```

This is already using PascalCase, so no change needed. Verify all other dictionary keys.

### 5. Code Snippet for ConfigManager Class Update

Here are the key changes required for the `ConfigManager` class:

```python
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
```

### 6. Testing

After implementing these changes, thorough testing is required to ensure all functionality works correctly with the new database schema:

1. Test loading configuration from the database
2. Test saving configuration to the database
3. Test migrating from file to database
4. Test all get/set methods for the different configuration types
5. Test interaction with the ModelManager class

## Migration Strategy

To ensure a smooth transition, we recommend the following approach:

1. Make a backup of the existing code and database
2. Implement the changes to the ConfigManager class
3. Create a new test database with the PascalCase schema
4. Test the updated ConfigManager with the new database
5. Once verified, migrate the production database using the migration script
6. Deploy the updated code

## Additional Considerations

- Ensure any other classes that interact with the database are also updated to use the PascalCase schema
- Update any documentation that references the database schema
- Communicate the changes to the development team
- Consider adding a version check to handle potential version mismatches between code and database

## Conclusion

By updating the ConfigManager class to work with the PascalCase database schema, we maintain consistency throughout the codebase and adhere to the AIDEV-PascalCase-1.2 standard. This change will improve code readability and maintainability while ensuring the unique visual signature of the project is preserved at all levels.
