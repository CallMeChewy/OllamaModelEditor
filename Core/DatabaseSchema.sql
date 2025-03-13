-- File: DatabaseSchema.sql
-- Path: OllamaModelEditor/Core/DatabaseSchema.sql
-- Standard: AIDEV-PascalCase-1.2
-- Created: 2025-03-12
-- Last Modified: 2025-03-12 08:45PM
-- Description: SQL schema for the OllamaModelEditor database

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
    ValueType TEXT,  -- For type conversion: "string", "int", "float", "bool", "json"
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application settings
CREATE TABLE IF NOT EXISTS AppSettings (
    Key TEXT PRIMARY KEY,
    Value TEXT,
    ValueType TEXT,  -- For type conversion
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
    Category TEXT,  -- e.g., "basic", "advanced"
    OrderIndex INTEGER  -- For display ordering
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
    GenerationTime REAL,  -- in seconds
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Benchmark results
CREATE TABLE IF NOT EXISTS BenchmarkResults (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    BenchmarkName TEXT,
    ModelName TEXT NOT NULL,
    ConfigID INTEGER,
    Prompt TEXT,
    AverageTime REAL,  -- Average generation time in seconds
    AverageTokens INTEGER,
    AverageTokensPerSecond REAL,
    Runs INTEGER,  -- Number of benchmark runs
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ConfigID) REFERENCES ModelConfigs(ID)
);

-- Messages for UI elements
CREATE TABLE IF NOT EXISTS UIMessages (
    Key TEXT PRIMARY KEY,
    Message TEXT NOT NULL,
    Context TEXT,  -- e.g., "error", "info", "tooltip"
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UI strings for internationalization
CREATE TABLE IF NOT EXISTS UIStrings (
    Key TEXT PRIMARY KEY,
    EnText TEXT NOT NULL,  -- English text
    Description TEXT,
    Context TEXT   -- Where this string is used
);
