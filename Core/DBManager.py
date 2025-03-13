# File: DBManager.py
# Path: OllamaModelEditor/Core/DBManager.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-12
# Last Modified: 2025-03-12 08:30PM
# Description: Database management for the OllamaModelEditor application

import os
import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import logging

class DBManager:
    """Manages the SQLite database for OllamaModelEditor."""
    
    def __init__(self, DBPath: Optional[str] = None):
        """
        Initialize the database manager.
        
        Args:
            DBPath: Optional path to database file
        """
        self.Logger = logging.getLogger('OllamaModelEditor.DBManager')
        
        # Set default database path if not provided
        if not DBPath:
            self.DBPath = self._GetDefaultDBPath()
        else:
            self.DBPath = DBPath
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.DBPath), exist_ok=True)
        
        # Initialize database
        self._InitializeDB()
    
    def _GetDefaultDBPath(self) -> str:
        """
        Determine the default database path based on the operating system.
        
        Returns:
            str: Path to the default database file
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
        
        return str(ConfigDir / 'OllamaModelEditor.db')
    
    def _InitializeDB(self) -> None:
        """Initialize the database with required tables and default data."""
        try:
            # Create schema definition
            Schema = """
            -- Database version
            CREATE TABLE IF NOT EXISTS DBVersion (
                Version INTEGER PRIMARY KEY,
                AppliedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Model configurations
            CREATE TABLE IF NOT EXISTS ModelConfigs (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ModelName TEXT NOT NULL,
                ConfigName TEXT NOT NULL,
                Temperature REAL DEFAULT 0.7,
                TopP REAL DEFAULT 0.9,
                MaxTokens INTEGER DEFAULT 2048,
                FrequencyPenalty REAL DEFAULT 0.0,
                PresencePenalty REAL DEFAULT 0.0,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                LastUsed TIMESTAMP,
                IsDefault BOOLEAN DEFAULT 0,
                UNIQUE(ModelName, ConfigName)
            );

            -- Preset configurations
            CREATE TABLE IF NOT EXISTS Presets (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT UNIQUE NOT NULL,
                Description TEXT,
                Temperature REAL DEFAULT 0.7,
                TopP REAL DEFAULT 0.9,
                MaxTokens INTEGER DEFAULT 2048,
                FrequencyPenalty REAL DEFAULT 0.0,
                PresencePenalty REAL DEFAULT 0.0,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                LastUsed TIMESTAMP
            );
            
            -- User-defined presets
            CREATE TABLE IF NOT EXISTS UserPresets (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT UNIQUE NOT NULL,
                Description TEXT,
                Temperature REAL DEFAULT 0.7,
                TopP REAL DEFAULT 0.9,
                MaxTokens INTEGER DEFAULT 2048,
                FrequencyPenalty REAL DEFAULT 0.0,
                PresencePenalty REAL DEFAULT 0.0,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                LastUsed TIMESTAMP
            );
            
            -- User preferences
            CREATE TABLE IF NOT EXISTS UserPreferences (
                Key TEXT PRIMARY KEY,
                Value TEXT,
                ValueType TEXT,
                UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Application settings
            CREATE TABLE IF NOT EXISTS AppSettings (
                Key TEXT PRIMARY KEY,
                Value TEXT,
                ValueType TEXT,
                Description TEXT,
                UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Parameter definitions and descriptions
            CREATE TABLE IF NOT EXISTS Parameters (
                Name TEXT PRIMARY KEY,
                DisplayName TEXT NOT NULL,
                Description TEXT,
                MinValue REAL,
                MaxValue REAL,
                DefaultValue REAL,
                StepSize REAL,
                IsInteger BOOLEAN DEFAULT 0,
                Category TEXT,
                OrderIndex INTEGER
            );
            
            -- Generation history
            CREATE TABLE IF NOT EXISTS GenerationHistory (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ModelName TEXT NOT NULL,
                Prompt TEXT NOT NULL,
                Response TEXT,
                Temperature REAL,
                TopP REAL,
                MaxTokens INTEGER,
                FrequencyPenalty REAL,
                PresencePenalty REAL,
                InputTokens INTEGER,
                OutputTokens INTEGER,
                TotalTokens INTEGER,
                GenerationTime REAL,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Benchmark results
            CREATE TABLE IF NOT EXISTS BenchmarkResults (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                BenchmarkName TEXT,
                ModelName TEXT NOT NULL,
                ConfigID INTEGER,
                Prompt TEXT,
                AverageTime REAL,
                AverageTokens INTEGER,
                AverageTokensPerSecond REAL,
                Runs INTEGER,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(ConfigID) REFERENCES ModelConfigs(ID)
            );
            
            -- Messages for UI elements
            CREATE TABLE IF NOT EXISTS UIMessages (
                Key TEXT PRIMARY KEY,
                Message TEXT NOT NULL,
                Context TEXT,
                UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- UI strings for internationalization
            CREATE TABLE IF NOT EXISTS UIStrings (
                Key TEXT PRIMARY KEY,
                EnText TEXT NOT NULL,
                Description TEXT,
                Context TEXT
            );
            """
            
            # Connect to database
            with sqlite3.connect(self.DBPath) as Conn:
                Cursor = Conn.cursor()
                
                # Execute schema script
                Cursor.executescript(Schema)
                
                # Check current database version
                Cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='DBVersion'")
                if Cursor.fetchone()[0] > 0:
                    Cursor.execute("SELECT MAX(Version) FROM DBVersion")
                    Result = Cursor.fetchone()
                    CurrentVersion = Result[0] if Result[0] is not None else 0
                else:
                    CurrentVersion = 0
                
                # Set initial version if it doesn't exist
                if CurrentVersion == 0:
                    Cursor.execute("INSERT INTO DBVersion (Version) VALUES (1)")
                    CurrentVersion = 1
                
                # Check if presets need to be initialized
                Cursor.execute("SELECT COUNT(*) FROM Presets")
                PresetCount = Cursor.fetchone()[0]
                
                if PresetCount == 0:
                    self._InitializePresets(Cursor)
                
                # Check if parameters need to be initialized
                Cursor.execute("SELECT COUNT(*) FROM Parameters")
                ParameterCount = Cursor.fetchone()[0]
                
                if ParameterCount == 0:
                    self._InitializeParameters(Cursor)
                
                # Check if UI strings need to be initialized
                Cursor.execute("SELECT COUNT(*) FROM UIStrings")
                UIStringCount = Cursor.fetchone()[0]
                
                if UIStringCount == 0:
                    self._InitializeUIStrings(Cursor)
                
                Conn.commit()
                
            self.Logger.info(f"Database initialized: {self.DBPath}")
                
        except sqlite3.Error as Error:
            self.Logger.error(f"Error initializing database: {Error}")
            raise
    
    def _InitializePresets(self, Cursor) -> None:
        """
        Initialize default presets.
        
        Args:
            Cursor: Database cursor
        """
        Presets = [
            (
                "Default", 
                "Balanced settings suitable for most tasks.", 
                0.7, 0.9, 2048, 0.0, 0.0
            ),
            (
                "Creative", 
                "Higher temperature and diversity for more creative, varied outputs.", 
                1.0, 0.95, 4096, 0.0, 0.0
            ),
            (
                "Precise", 
                "Lower temperature for more focused, deterministic responses.", 
                0.3, 0.7, 2048, 0.5, 0.0
            ),
            (
                "Fast", 
                "Optimized for speed with shorter outputs.", 
                0.7, 0.9, 1024, 0.0, 0.0
            ),
            (
                "Balanced", 
                "Moderate settings with some repetition control for well-rounded responses.", 
                0.6, 0.85, 2048, 0.3, 0.3
            ),
            (
                "Deterministic", 
                "Minimal randomness for highly predictable, consistent outputs.", 
                0.0, 0.5, 2048, 0.0, 0.0
            )
        ]
        
        Cursor.executemany(
            """
            INSERT INTO Presets (Name, Description, Temperature, TopP, MaxTokens, 
                               FrequencyPenalty, PresencePenalty)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, 
            Presets
        )
    
    def _InitializeParameters(self, Cursor) -> None:
        """
        Initialize parameter definitions.
        
        Args:
            Cursor: Database cursor
        """
        Parameters = [
            (
                "Temperature", "Temperature", 
                "Controls randomness in text generation. Higher values (0.7-1.0) produce more creative outputs, while lower values (0.2-0.5) make output more focused and deterministic.",
                0.0, 2.0, 0.7, 0.1, 0, "basic", 1
            ),
            (
                "TopP", "Top-P",
                "Controls diversity via nucleus sampling. Lower values make output more focused on likely tokens. 0.9 is a good starting point.",
                0.0, 1.0, 0.9, 0.01, 0, "basic", 2
            ),
            (
                "MaxTokens", "Max Tokens",
                "The maximum length of the generated text. Higher values allow for longer responses but consume more resources.",
                1, 32000, 2048, 1, 1, "basic", 3
            ),
            (
                "FrequencyPenalty", "Frequency Penalty",
                "Reduces repetition by penalizing tokens that have already appeared in the text. Higher values (0.5-1.0) strongly discourage repetition.",
                0.0, 2.0, 0.0, 0.1, 0, "advanced", 4
            ),
            (
                "PresencePenalty", "Presence Penalty",
                "Penalizes tokens that have appeared at all, encouraging the model to discuss new topics. Useful for keeping responses diverse.",
                0.0, 2.0, 0.0, 0.1, 0, "advanced", 5
            )
        ]
        
        Cursor.executemany(
            """
            INSERT INTO Parameters (Name, DisplayName, Description, MinValue, MaxValue, 
                                 DefaultValue, StepSize, IsInteger, Category, OrderIndex)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, 
            Parameters
        )
    
    def _InitializeUIStrings(self, Cursor) -> None:
        """
        Initialize UI strings.
        
        Args:
            Cursor: Database cursor
        """
        # Example UI strings initialization
        UIStrings = [
            ("app.title", "Ollama Model Editor", "Main window title", "window"),
            ("menu.file", "File", "File menu", "menu"),
            ("menu.edit", "Edit", "Edit menu", "menu"),
            ("menu.view", "View", "View menu", "menu"),
            ("menu.tools", "Tools", "Tools menu", "menu"),
            ("menu.help", "Help", "Help menu", "menu"),
            ("button.apply", "Apply Changes", "Apply button", "button"),
            ("button.reset", "Reset to Default", "Reset button", "button"),
            ("error.no_model", "Please select a model first.", "Error message", "error"),
            ("label.parameter_editor", "Parameter Editor", "Tab label", "tab"),
            ("label.benchmark", "Benchmark", "Tab label", "tab"),
            ("label.analysis", "Analysis", "Tab label", "tab"),
            ("label.temperature", "Temperature:", "Parameter label", "parameter"),
            ("label.top_p", "Top-P:", "Parameter label", "parameter"),
            ("label.max_tokens", "Max Tokens:", "Parameter label", "parameter"),
            ("label.frequency_penalty", "Frequency Penalty:", "Parameter label", "parameter"),
            ("label.presence_penalty", "Presence Penalty:", "Parameter label", "parameter"),
            ("label.model_library", "Model Library", "Dock title", "dock"),
            ("label.presets", "Preset:", "Presets label", "parameter"),
            ("label.available_models", "Available Models:", "Model list label", "label"),
            ("status.loading_models", "Loading models...", "Status message", "status"),
            ("status.models_loaded", "Loaded {0} models", "Status message", "status"),
            ("status.model_selected", "Model {0} selected", "Status message", "status"),
            ("status.api_connected", "API: Connected", "Status message", "status"),
            ("status.api_error", "API: Error", "Status message", "status"),
            ("status.no_connection", "API: Not connected", "Status message", "status")
        ]
        
        Cursor.executemany(
            """
            INSERT INTO UIStrings (Key, EnText, Description, Context)
            VALUES (?, ?, ?, ?)
            """, 
            UIStrings
        )
    
    def GetConnection(self) -> sqlite3.Connection:
        """
        Get a database connection.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        return sqlite3.connect(self.DBPath)
    
    def ExecuteQuery(self, Query: str, Params: tuple = ()) -> List[tuple]:
        """
        Execute a query and return results.
        
        Args:
            Query: SQL query
            Params: Query parameters
            
        Returns:
            List of result tuples
        """
        try:
            with self.GetConnection() as Conn:
                Cursor = Conn.cursor()
                Cursor.execute(Query, Params)
                return Cursor.fetchall()
        except sqlite3.Error as Error:
            self.Logger.error(f"Error executing query: {Error}")
            self.Logger.debug(f"Query: {Query}, Params: {Params}")
            raise
    
    def ExecuteNonQuery(self, Query: str, Params: tuple = ()) -> int:
        """
        Execute a non-query statement.
        
        Args:
            Query: SQL statement
            Params: Statement parameters
            
        Returns:
            Row count or last row ID
        """
        try:
            with self.GetConnection() as Conn:
                Cursor = Conn.cursor()
                Cursor.execute(Query, Params)
                Conn.commit()
                return Cursor.lastrowid or Cursor.rowcount
        except sqlite3.Error as Error:
            self.Logger.error(f"Error executing non-query: {Error}")
            self.Logger.debug(f"Query: {Query}, Params: {Params}")
            raise
    
    # Model Configuration Methods
    
    def GetModelConfigs(self, ModelName: str) -> List[Dict[str, Any]]:
        """
        Get all configurations for a model.
        
        Args:
            ModelName: Name of the model
            
        Returns:
            List of configuration dictionaries
        """
        Results = self.ExecuteQuery(
            "SELECT * FROM ModelConfigs WHERE ModelName = ?",
            (ModelName,)
        )
        
        Columns = [
            "ID", "ModelName", "ConfigName", "Temperature", "TopP", 
            "MaxTokens", "FrequencyPenalty", "PresencePenalty", 
            "CreatedAt", "LastUsed", "IsDefault"
        ]
        
        return [dict(zip(Columns, Row)) for Row in Results]
    
    def GetModelConfig(self, ModelName: str, ConfigName: str = "Default") -> Optional[Dict[str, Any]]:
        """
        Get a specific configuration for a model.
        
        Args:
            ModelName: Name of the model
            ConfigName: Name of the configuration
            
        Returns:
            Configuration dictionary or None if not found
        """
        Results = self.ExecuteQuery(
            "SELECT * FROM ModelConfigs WHERE ModelName = ? AND ConfigName = ?",
            (ModelName, ConfigName)
        )
        
        if not Results:
            return None
        
        Columns = [
            "ID", "ModelName", "ConfigName", "Temperature", "TopP", 
            "MaxTokens", "FrequencyPenalty", "PresencePenalty", 
            "CreatedAt", "LastUsed", "IsDefault"
        ]
        
        return dict(zip(Columns, Results[0]))
    
    def SaveModelConfig(self, ModelName: str, ConfigName: str, Params: Dict[str, Any]) -> int:
        """
        Save a model configuration.
        
        Args:
            ModelName: Name of the model
            ConfigName: Name of the configuration
            Params: Configuration parameters
            
        Returns:
            Row ID of the saved configuration
        """
        # Check if configuration exists
        ExistingConfig = self.GetModelConfig(ModelName, ConfigName)
        
        if ExistingConfig:
            # Update existing configuration
            Query = """
            UPDATE ModelConfigs
            SET Temperature = ?, TopP = ?, MaxTokens = ?, 
                FrequencyPenalty = ?, PresencePenalty = ?,
                LastUsed = CURRENT_TIMESTAMP
            WHERE ModelName = ? AND ConfigName = ?
            """
            
            self.ExecuteNonQuery(
                Query,
                (
                    Params.get('Temperature', 0.7),
                    Params.get('TopP', 0.9),
                    Params.get('MaxTokens', 2048),
                    Params.get('FrequencyPenalty', 0.0),
                    Params.get('PresencePenalty', 0.0),
                    ModelName,
                    ConfigName
                )
            )
            
            return ExistingConfig["ID"]
        else:
            # Insert new configuration
            Query = """
            INSERT INTO ModelConfigs
            (ModelName, ConfigName, Temperature, TopP, MaxTokens, 
             FrequencyPenalty, PresencePenalty)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            return self.ExecuteNonQuery(
                Query,
                (
                    ModelName,
                    ConfigName,
                    Params.get('Temperature', 0.7),
                    Params.get('TopP', 0.9),
                    Params.get('MaxTokens', 2048),
                    Params.get('FrequencyPenalty', 0.0),
                    Params.get('PresencePenalty', 0.0)
                )
            )
    
    def DeleteModelConfig(self, ModelName: str, ConfigName: str) -> bool:
        """
        Delete a model configuration.
        
        Args:
            ModelName: Name of the model
            ConfigName: Name of the configuration
            
        Returns:
            True if deleted, False if not found
        """
        Result = self.ExecuteNonQuery(
            "DELETE FROM ModelConfigs WHERE ModelName = ? AND ConfigName = ?",
            (ModelName, ConfigName)
        )
        
        return Result > 0
    
    # Preset Methods
    
    def GetPresets(self) -> List[Dict[str, Any]]:
        """
        Get all preset configurations.
        
        Returns:
            List of preset dictionaries
        """
        Results = self.ExecuteQuery("SELECT * FROM Presets ORDER BY Name")
        
        Columns = [
            "ID", "Name", "Description", "Temperature", "TopP", 
            "MaxTokens", "FrequencyPenalty", "PresencePenalty", 
            "CreatedAt", "LastUsed"
        ]
        
        return [dict(zip(Columns, Row)) for Row in Results]
    
    def GetPreset(self, PresetName: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific preset configuration.
        
        Args:
            PresetName: Name of the preset
            
        Returns:
            Preset dictionary or None if not found
        """
        Results = self.ExecuteQuery(
            "SELECT * FROM Presets WHERE Name = ?",
            (PresetName,)
        )
        
        if not Results:
            return None
        
        Columns = [
            "ID", "Name", "Description", "Temperature", "TopP", 
            "MaxTokens", "FrequencyPenalty", "PresencePenalty", 
            "CreatedAt", "LastUsed"
        ]
        
        return dict(zip(Columns, Results[0]))
    
    def UpdatePresetUsage(self, PresetName: str) -> bool:
        """
        Update the LastUsed timestamp for a preset.
        
        Args:
            PresetName: Name of the preset
            
        Returns:
            True if updated, False if not found
        """
        Result = self.ExecuteNonQuery(
            "UPDATE Presets SET LastUsed = CURRENT_TIMESTAMP WHERE Name = ?",
            (PresetName,)
        )
        
        return Result > 0
    
    # User-defined Preset Methods
    
    def GetUserPresets(self) -> List[Dict[str, Any]]:
        """
        Get all user-defined presets.
        
        Returns:
            List of user preset dictionaries
        """
        Results = self.ExecuteQuery("SELECT * FROM UserPresets ORDER BY Name")
        
        Columns = [
            "ID", "Name", "Description", "Temperature", "TopP", 
            "MaxTokens", "FrequencyPenalty", "PresencePenalty", 
            "CreatedAt", "LastUsed"
        ]
        
        return [dict(zip(Columns, Row)) for Row in Results]
    
    def SaveUserPreset(self, PresetName: str, Description: str, Params: Dict[str, Any]) -> int:
        """
        Save a user-defined preset.
        
        Args:
            PresetName: Name of the preset
            Description: Preset description
            Params: Preset parameters
            
        Returns:
            Row ID of the saved preset
        """
        # Check if preset exists
        ExistingPreset = self.ExecuteQuery(
            "SELECT ID FROM UserPresets WHERE Name = ?",
            (PresetName,)
        )
        
        if ExistingPreset:
            # Update existing preset
            Query = """
            UPDATE UserPresets
            SET Description = ?, Temperature = ?, TopP = ?, MaxTokens = ?, 
                FrequencyPenalty = ?, PresencePenalty = ?,
                LastUsed = CURRENT_TIMESTAMP
            WHERE Name = ?
            """
            
            self.ExecuteNonQuery(
                Query,
                (
                    Description,
                    Params.get('Temperature', 0.7),
                    Params.get('TopP', 0.9),
                    Params.get('MaxTokens', 2048),
                    Params.get('FrequencyPenalty', 0.0),
                    Params.get('PresencePenalty', 0.0),
                    PresetName
                )
            )
            
            return ExistingPreset[0][0]
        else:
            # Insert new preset
            Query = """
            INSERT INTO UserPresets
            (Name, Description, Temperature, TopP, MaxTokens, 
             FrequencyPenalty, PresencePenalty)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            return self.ExecuteNonQuery(
                Query,
                (
                    PresetName,
                    Description,
                    Params.get('Temperature', 0.7),
                    Params.get('TopP', 0.9),
                    Params.get('MaxTokens', 2048),
                    Params.get('FrequencyPenalty', 0.0),
                    Params.get('PresencePenalty', 0.0)
                )
            )
    
    def DeleteUserPreset(self, PresetName: str) -> bool:
        """
        Delete a user-defined preset.
        
        Args:
            PresetName: Name of the preset
            
        Returns:
            True if deleted, False if not found
        """
        Result = self.ExecuteNonQuery(
            "DELETE FROM UserPresets WHERE Name = ?",
            (PresetName,)
        )
        
        return Result > 0
    
    # User Preference Methods
    
    def GetUserPreference(self, Key: str, Default: Any = None) -> Any:
        """
        Get a user preference.
        
        Args:
            Key: Preference key
            Default: Default value if preference not found
            
        Returns:
            Preference value
        """
        Results = self.ExecuteQuery(
            "SELECT Value, ValueType FROM UserPreferences WHERE Key = ?",
            (Key,)
        )
        
        if not Results:
            return Default
        
        Value, ValueType = Results[0]
        
        # Convert value based on type
        if ValueType == "int":
            return int(Value)
        elif ValueType == "float":
            return float(Value)
        elif ValueType == "bool":
            return Value.lower() in ("true", "1", "yes")
        elif ValueType == "json":
            return json.loads(Value)
        else:
            return Value
    
    def SetUserPreference(self, Key: str, Value: Any) -> None:
        """
        Set a user preference.
        
        Args:
            Key: Preference key
            Value: Preference value
        """
        # Determine value type
        if isinstance(Value, bool):
            ValueStr = "true" if Value else "false"
            ValueType = "bool"
        elif isinstance(Value, int):
            ValueStr = str(Value)
            ValueType = "int"
        elif isinstance(Value, float):
            ValueStr = str(Value)
            ValueType = "float"
        elif isinstance(Value, (dict, list)):
            ValueStr = json.dumps(Value)
            ValueType = "json"
        else:
            ValueStr = str(Value)
            ValueType = "string"
        
        # Check if preference exists
        Results = self.ExecuteQuery(
            "SELECT COUNT(*) FROM UserPreferences WHERE Key = ?",
            (Key,)
        )
        
        if Results[0][0] > 0:
            # Update existing preference
            self.ExecuteNonQuery(
                """
                UPDATE UserPreferences
                SET Value = ?, ValueType = ?, UpdatedAt = CURRENT_TIMESTAMP
                WHERE Key = ?
                """,
                (ValueStr, ValueType, Key)
            )
        else:
            # Insert new preference
            self.ExecuteNonQuery(
                """
                INSERT INTO UserPreferences (Key, Value, ValueType)
                VALUES (?, ?, ?)
                """,
                (Key, ValueStr, ValueType)
            )
    
    # App Settings Methods
    
    def GetAppSetting(self, Key: str, Default: Any = None) -> Any:
        """
        Get an application setting.
        
        Args:
            Key: Setting key
            Default: Default value if setting not found
            
        Returns:
            Setting value
        """
        Results = self.ExecuteQuery(
            "SELECT Value, ValueType FROM AppSettings WHERE Key = ?",
            (Key,)
        )
        
        if not Results:
            return Default
        
        Value, ValueType = Results[0]
        
        # Convert value based on type
        if ValueType == "int":
            return int(Value)
        elif ValueType == "float":
            return float(Value)
        elif ValueType == "bool":
            return Value.lower() in ("true", "1", "yes")
        elif ValueType == "json":
            return json.loads(Value)
        else:
            return Value
    
    def SetAppSetting(self, Key: str, Value: Any, Description: str = None) -> None:
        """
        Set an application setting.
        
        Args:
            Key: Setting key
            Value: Setting value
            Description: Optional setting description
        """
        # Determine value type
        if isinstance(Value, bool):
            ValueStr = "true" if Value else "false"
            ValueType = "bool"
        elif isinstance(Value, int):
            ValueStr = str(Value)
            ValueType = "int"
        elif isinstance(Value, float):
            ValueStr = str(Value)
            ValueType = "float"
        elif isinstance(Value, (dict, list)):
            ValueStr = json.dumps(Value)
            ValueType = "json"
        else:
            ValueStr = str(Value)
            ValueType = "string"
        
        # Check if setting exists
        Results = self.ExecuteQuery(
            "SELECT COUNT(*) FROM AppSettings WHERE Key = ?",
            (Key,)
        )
        
        if Results[0][0] > 0:
            # Update existing setting
            if Description:
                self.ExecuteNonQuery(
                    """
                    UPDATE AppSettings
                    SET Value = ?, ValueType = ?, Description = ?, UpdatedAt = CURRENT_TIMESTAMP
                    WHERE Key = ?
                    """,
                    (ValueStr, ValueType, Description, Key)
                )
            else:
                self.ExecuteNonQuery(
                    """
                    UPDATE AppSettings
                    SET Value = ?, ValueType = ?, UpdatedAt = CURRENT_TIMESTAMP
                    WHERE Key = ?
                    """,
                    (ValueStr, ValueType, Key)
                )
        else:
            # Insert new setting
            self.ExecuteNonQuery(
                """
                INSERT INTO AppSettings (Key, Value, ValueType, Description)
                VALUES (?, ?, ?, ?)
                """,
                (Key, ValueStr, ValueType, Description)
            )
    
    # UI String Methods
    
    def GetUIString(self, Key: str, Default: str = None) -> str:
        """
        Get a UI string.
        
        Args:
            Key: String key
            Default: Default value if string not found
            
        Returns:
            UI string
        """
        Results = self.ExecuteQuery(
            "SELECT EnText FROM UIStrings WHERE Key = ?",
            (Key,)
        )
        
        if not Results:
            return Default or Key
        
        return Results[0][0]
    
    def GetUIStrings(self, Context: str = None) -> Dict[str, str]:
        """
        Get all UI strings, optionally filtered by context.
        
        Args:
            Context: Optional context filter
            
        Returns:
            Dictionary of UI strings (key -> text)
        """
        if Context:
            Results = self.ExecuteQuery(
                "SELECT Key, EnText FROM UIStrings WHERE Context = ?",
                (Context,)
            )
        else:
            Results = self.ExecuteQuery(
                "SELECT Key, EnText FROM UIStrings"
            )
        
        return {Key: Text for Key, Text in Results}
    
    def SetUIString(self, Key: str, Text: str, Description: str = None, Context: str = None) -> None:
        """
        Set a UI string.
        
        Args:
            Key: String key
            Text: String text (English)
            Description: Optional description
            Context: Optional context
        """
        # Check if string exists
        Results = self.ExecuteQuery(
            "SELECT COUNT(*) FROM UIStrings WHERE Key = ?",
            (Key,)
        )
        
        if Results[0][0] > 0:
            # Update existing string
            if Description and Context:
                self.ExecuteNonQuery(
                    """
                    UPDATE UIStrings
                    SET EnText = ?, Description = ?, Context = ?
                    WHERE Key = ?
                    """,
                    (Text, Description, Context, Key)
                )
            elif Description:
                self.ExecuteNonQuery(
                    """
                    UPDATE UIStrings
                    SET EnText = ?, Description = ?
                    WHERE Key = ?
                    """,
                    (Text, Description, Key)
                )
            elif Context:
                self.ExecuteNonQuery(
                    """
                    UPDATE UIStrings
                    SET EnText = ?, Context = ?
                    WHERE Key = ?
                    """,
                    (Text, Context, Key)
                )
            else:
                self.ExecuteNonQuery(
                    """
                    UPDATE UIStrings
                    SET EnText = ?
                    WHERE Key = ?
                    """,
                    (Text, Key)
                )
        else:
            # Insert new string
            self.ExecuteNonQuery(
                """
                INSERT INTO UIStrings (Key, EnText, Description, Context)
                VALUES (?, ?, ?, ?)
                """,
                (Key, Text, Description, Context)
            )
    
    # Parameter Methods
    
    def GetAllParameters(self) -> List[Dict[str, Any]]:
        """
        Get all parameter definitions.
        
        Returns:
            List of parameter dictionaries
        """
        Results = self.ExecuteQuery(
            """
            SELECT * FROM Parameters
            ORDER BY OrderIndex
            """
        )
        
        Columns = [
            "Name", "DisplayName", "Description", "MinValue", "MaxValue",
            "DefaultValue", "StepSize", "IsInteger", "Category", "OrderIndex"
        ]
        
        return [dict(zip(Columns, Row)) for Row in Results]
    
    def GetParametersByCategory(self, Category: str) -> List[Dict[str, Any]]:
        """
        Get parameter definitions by category.
        
        Args:
            Category: Parameter category
            
        Returns:
            List of parameter dictionaries
        """
        Results = self.ExecuteQuery(
            """
            SELECT * FROM Parameters
            WHERE Category = ?
            ORDER BY OrderIndex
            """,
            (Category,)
        )
        
        Columns = [
            "Name", "DisplayName", "Description", "MinValue", "MaxValue",
            "DefaultValue", "StepSize", "IsInteger", "Category", "OrderIndex"
        ]
        
        return [dict(zip(Columns, Row)) for Row in Results]
    
    def GetParameter(self, Name: str) -> Optional[Dict[str, Any]]:
        """
        Get a parameter definition.
        
        Args:
            Name: Parameter name
            
        Returns:
            Parameter dictionary or None if not found
        """
        Results = self.ExecuteQuery(
            """
            SELECT * FROM Parameters
            WHERE Name = ?
            """,
            (Name,)
        )
        
        if not Results:
            return None
        
        Columns = [
            "Name", "DisplayName", "Description", "MinValue", "MaxValue",
            "DefaultValue", "StepSize", "IsInteger", "Category", "OrderIndex"
        ]
        
        return dict(zip(Columns, Results[0]))
    
    # Generation History Methods
    
    def AddGenerationHistory(self, ModelName: str, Prompt: str, Response: str, 
                             Params: Dict[str, Any], Metrics: Dict[str, Any]) -> int:
        """
        Add a generation history entry.
        
        Args:
            ModelName: Name of the model
            Prompt: Input prompt
            Response: Generated response
            Params: Generation parameters
            Metrics: Generation metrics
            
        Returns:
            ID of the new history entry
        """
        Query = """
        INSERT INTO GenerationHistory (
            ModelName, Prompt, Response, Temperature, TopP, MaxTokens,
            FrequencyPenalty, PresencePenalty, InputTokens, OutputTokens,
            TotalTokens, GenerationTime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        return self.ExecuteNonQuery(
            Query,
            (
                ModelName,
                Prompt,
                Response,
                Params.get('Temperature', 0.7),
                Params.get('TopP', 0.9),
                Params.get('MaxTokens', 2048),
                Params.get('FrequencyPenalty', 0.0),
                Params.get('PresencePenalty', 0.0),
                Metrics.get('InputTokens', 0),
                Metrics.get('OutputTokens', 0),
                Metrics.get('TotalTokens', 0),
                Metrics.get('GenerationTime', 0.0)
            )
        )
    
    def GetGenerationHistory(self, Limit: int = 100, Offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get generation history entries.
        
        Args:
            Limit: Maximum number of entries to retrieve
            Offset: Offset for pagination
            
        Returns:
            List of history entry dictionaries
        """
        Results = self.ExecuteQuery(
            """
            SELECT * FROM GenerationHistory
            ORDER BY CreatedAt DESC
            LIMIT ? OFFSET ?
            """,
            (Limit, Offset)
        )
        
        Columns = [
            "ID", "ModelName", "Prompt", "Response", "Temperature",
            "TopP", "MaxTokens", "FrequencyPenalty", "PresencePenalty",
            "InputTokens", "OutputTokens", "TotalTokens",
            "GenerationTime", "CreatedAt"
        ]
        
        return [dict(zip(Columns, Row)) for Row in Results]
    
    def GetGenerationHistoryForModel(self, ModelName: str, Limit: int = 100, Offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get generation history entries for a specific model.
        
        Args:
            ModelName: Name of the model
            Limit: Maximum number of entries to retrieve
            Offset: Offset for pagination
            
        Returns:
            List of history entry dictionaries
        """
        Results = self.ExecuteQuery(
            """
            SELECT * FROM GenerationHistory
            WHERE ModelName = ?
            ORDER BY CreatedAt DESC
            LIMIT ? OFFSET ?
            """,
            (ModelName, Limit, Offset)
        )
        
        Columns = [
            "ID", "ModelName", "Prompt", "Response", "Temperature",
            "TopP", "MaxTokens", "FrequencyPenalty", "PresencePenalty",
            "InputTokens", "OutputTokens", "TotalTokens",
            "GenerationTime", "CreatedAt"
        ]
        
        return [dict(zip(Columns, Row)) for Row in Results]
    
    def ClearGenerationHistory(self) -> int:
        """
        Clear all generation history.
        
        Returns:
            Number of entries deleted
        """
        return self.ExecuteNonQuery("DELETE FROM GenerationHistory")
    
    # Benchmark Methods
    
    def AddBenchmarkResult(self, BenchmarkName: str, ModelName: str, Prompt: str,
                          AverageTime: float, AverageTokens: int, TokensPerSecond: float,
                          Runs: int, ConfigParams: Dict[str, Any]) -> int:
        """
        Add a benchmark result.
        
        Args:
            BenchmarkName: Name of the benchmark
            ModelName: Name of the model
            Prompt: Benchmark prompt
            AverageTime: Average generation time (seconds)
            AverageTokens: Average number of tokens
            TokensPerSecond: Average tokens per second
            Runs: Number of benchmark runs
            ConfigParams: Configuration parameters used
            
        Returns:
            ID of the new benchmark result
        """
        # Save model configuration
        ConfigID = self.SaveModelConfig(ModelName, f"Benchmark-{BenchmarkName}", ConfigParams)
        
        Query = """
        INSERT INTO BenchmarkResults (
            BenchmarkName, ModelName, ConfigID, Prompt,
            AverageTime, AverageTokens, AverageTokensPerSecond, Runs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        return self.ExecuteNonQuery(
            Query,
            (
                BenchmarkName,
                ModelName,
                ConfigID,
                Prompt,
                AverageTime,
                AverageTokens,
                TokensPerSecond,
                Runs
            )
        )
    
    def GetBenchmarkResults(self, ModelName: str = None) -> List[Dict[str, Any]]:
        """
        Get benchmark results, optionally filtered by model.
        
        Args:
            ModelName: Optional model name filter
            
        Returns:
            List of benchmark result dictionaries
        """
        if ModelName:
            Results = self.ExecuteQuery(
                """
                SELECT b.*, c.Temperature, c.TopP, c.MaxTokens, 
                       c.FrequencyPenalty, c.PresencePenalty
                FROM BenchmarkResults b
                JOIN ModelConfigs c ON b.ConfigID = c.ID
                WHERE b.ModelName = ?
                ORDER BY b.CreatedAt DESC
                """,
                (ModelName,)
            )
        else:
            Results = self.ExecuteQuery(
                """
                SELECT b.*, c.Temperature, c.TopP, c.MaxTokens, 
                       c.FrequencyPenalty, c.PresencePenalty
                FROM BenchmarkResults b
                JOIN ModelConfigs c ON b.ConfigID = c.ID
                ORDER BY b.CreatedAt DESC
                """
            )
        
        Columns = [
            "ID", "BenchmarkName", "ModelName", "ConfigID", "Prompt",
            "AverageTime", "AverageTokens", "AverageTokensPerSecond", "Runs",
            "CreatedAt", "Temperature", "TopP", "MaxTokens",
            "FrequencyPenalty", "PresencePenalty"
        ]
        
        return [dict(zip(Columns, Row)) for Row in Results]
    
    # Database Utility Methods
    
    def BackupDatabase(self, BackupPath: str) -> bool:
        """
        Create a backup of the database.
        
        Args:
            BackupPath: Path for the backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(BackupPath), exist_ok=True)
            
            # Connect to source database
            SourceConn = sqlite3.connect(self.DBPath)
            
            # Connect to backup database
            BackupConn = sqlite3.connect(BackupPath)
            
            # Copy database content
            SourceConn.backup(BackupConn)
            
            # Close connections
            SourceConn.close()
            BackupConn.close()
            
            self.Logger.info(f"Database backed up to: {BackupPath}")
            return True
        
        except sqlite3.Error as Error:
            self.Logger.error(f"Error backing up database: {Error}")
            return False
    
    def RestoreDatabase(self, BackupPath: str) -> bool:
        """
        Restore the database from a backup.
        
        Args:
            BackupPath: Path to the backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(BackupPath):
                self.Logger.error(f"Backup file not found: {BackupPath}")
                return False
            
            # Close any open connections
            try:
                self.GetConnection().close()
            except:
                pass
            
            # Connect to backup database
            BackupConn = sqlite3.connect(BackupPath)
            
            # Connect to target database
            TargetConn = sqlite3.connect(self.DBPath)
            
            # Copy database content
            BackupConn.backup(TargetConn)
            
            # Close connections
            BackupConn.close()
            TargetConn.close()
            
            self.Logger.info(f"Database restored from: {BackupPath}")
            return True
        
        except sqlite3.Error as Error:
            self.Logger.error(f"Error restoring database: {Error}")
            return False