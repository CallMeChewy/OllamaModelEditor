#!/usr/bin/env python3
# File: MigrateToDatabase.py
# Path: OllamaModelEditor/scripts/MigrateToDatabase.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-12
# Last Modified: 2025-03-12 06:30PM
# Description: Migrates configuration from files to SQLite database

import os
import sys
import json
import yaml
import argparse
from pathlib import Path

# Add project root to path
ProjectRoot = Path(__file__).resolve().parents[1]
sys.path.append(str(ProjectRoot))

try:
    from Core.DBManager import DBManager
    from Core.ConfigManager import ConfigManager
except ImportError as Error:
    print(f"Error importing required modules: {Error}")
    print("Make sure you're running this script from the OllamaModelEditor directory")
    sys.exit(1)

def MigrateToDatabase(ConfigPath=None, DBPath=None):
    """
    Migrate configuration from files to database.
    
    Args:
        ConfigPath: Optional path to configuration file
        DBPath: Optional path to database file
    """
    print("\nOllamaModelEditor - Configuration Migration Tool")
    print("==============================================\n")
    print("This tool will migrate your configuration from files to the SQLite database.")
    print("Your existing configuration files will not be modified.")
    
    # Initialize database
    try:
        print("\nInitializing database...")
        DB = DBManager(DBPath)
        print(f"Database initialized: {DB.DBPath}")
    except Exception as Error:
        print(f"Error initializing database: {Error}")
        sys.exit(1)
    
    # Initialize file-based configuration
    try:
        print("\nLoading configuration files...")
        Config = ConfigManager(ConfigPath)
        Success = Config.LoadConfig()
        
        if Success:
            print("Configuration loaded successfully.")
        else:
            print("Warning: Configuration loaded with default values.")
    except Exception as Error:
        print(f"Error loading configuration: {Error}")
        sys.exit(1)
    
    # Start migration
    print("\nStarting migration...")
    
    print("\nMigrating application settings...")
    SuccessCount = 0
    TotalCount = len(Config.AppConfig)
    
    # Migrate application settings
    for Key, Value in Config.AppConfig.items():
        try:
            DB.SetAppSetting(Key, Value)
            SuccessCount += 1
            print(f"  • Setting migrated: {Key}")
        except Exception as Error:
            print(f"  × Error migrating setting {Key}: {Error}")
    
    print(f"Migrated {SuccessCount} of {TotalCount} application settings.")
    
    print("\nMigrating user preferences...")
    SuccessCount = 0
    TotalCount = len(Config.UserPreferences)
    
    # Migrate user preferences
    for Key, Value in Config.UserPreferences.items():
        try:
            DB.SetUserPreference(Key, Value)
            SuccessCount += 1
            print(f"  • Preference migrated: {Key}")
        except Exception as Error:
            print(f"  × Error migrating preference {Key}: {Error}")
    
    print(f"Migrated {SuccessCount} of {TotalCount} user preferences.")
    
    print("\nMigrating model configurations...")
    SuccessCount = 0
    TotalCount = 0
    
    # Count total configurations
    for ModelName, ModelConfig in Config.ModelConfigs.items():
        if isinstance(ModelConfig, dict) and not isinstance(list(ModelConfig.values())[0], dict):
            TotalCount += 1
        else:
            TotalCount += len(ModelConfig)
    
    # Migrate model configurations
    for ModelName, ModelConfig in Config.ModelConfigs.items():
        try:
            if isinstance(ModelConfig, dict) and not isinstance(list(ModelConfig.values())[0], dict):
                # This is a single configuration (not a dict of configs)
                DB.SaveModelConfig(ModelName, "Default", ModelConfig)
                SuccessCount += 1
                print(f"  • Model configuration migrated: {ModelName}")
            else:
                # This is a dict of configurations
                for ConfigName, ConfigParams in ModelConfig.items():
                    DB.SaveModelConfig(ModelName, ConfigName, ConfigParams)
                    SuccessCount += 1
                    print(f"  • Model configuration migrated: {ModelName}/{ConfigName}")
        except Exception as Error:
            print(f"  × Error migrating model configuration {ModelName}: {Error}")
    
    print(f"Migrated {SuccessCount} of {TotalCount} model configurations.")
    
    print("\nMigration completed successfully!")
    print(f"Database path: {DB.DBPath}")
    print("\nYou can now use the database for configuration storage.")
    print("To use the database, run the application with the --db flag:")
    print(f"  python Main.py --db {DB.DBPath}")

def ParseCommandLine():
    """
    Parse command line arguments.
    
    Returns:
        Namespace with parsed arguments
    """
    Parser = argparse.ArgumentParser(description="OllamaModelEditor - Configuration Migration Tool")
    Parser.add_argument("--config", help="Path to configuration file")
    Parser.add_argument("--db", help="Path to database file")
    return Parser.parse_args()

if __name__ == "__main__":
    Args = ParseCommandLine()
    MigrateToDatabase(Args.config, Args.db)
