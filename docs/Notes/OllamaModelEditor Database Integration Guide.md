# OllamaModelEditor Database Integration Guide

## Overview

This guide explains how the OllamaModelEditor application integrates with its SQLite database and provides information about the PascalCase naming convention used in the database schema.

## Database Schema

The OllamaModelEditor application uses a SQLite database with a schema that follows the AIDEV-PascalCase-1.2 standard. This means all table and column names use PascalCase (e.g., `ModelConfigs`, `ModelName`) instead of the more common snake_case (e.g., `model_configs`, `model_name`).

### Main Tables

- **ModelConfigs**: Stores model configurations
  - **ID**: Primary key
  - **ModelName**: Name of the model
  - **ConfigName**: Name of the configuration
  - **Temperature**: Model temperature parameter
  - **TopP**: Top-P parameter
  - **MaxTokens**: Maximum tokens parameter
  - **FrequencyPenalty**: Frequency penalty parameter
  - **PresencePenalty**: Presence penalty parameter
  - **CreatedAt**: Creation timestamp
  - **LastUsed**: Last usage timestamp
  - **IsDefault**: Flag for default configuration

- **Presets**: Stores predefined parameter presets
  - **ID**: Primary key
  - **Name**: Preset name
  - **Description**: Preset description
  - **Temperature**, **TopP**, **MaxTokens**, etc.: Parameter values

- **UserPresets**: Stores user-defined parameter presets
  - Similar structure to Presets

- **UserPreferences**: Stores user preferences
  - **Key**: Preference key
  - **Value**: Preference value
  - **ValueType**: Type of the value for conversion
  - **UpdatedAt**: Last update timestamp

- **AppSettings**: Stores application settings
  - Similar structure to UserPreferences

- **GenerationHistory**: Stores history of text generations
  - **ID**: Primary key
  - **ModelName**: Model used
  - **Prompt**: Input prompt
  - **Response**: Generated response
  - **Temperature**, **TopP**, etc.: Parameters used
  - **InputTokens**, **OutputTokens**, etc.: Metrics
  - **CreatedAt**: Timestamp

- **BenchmarkResults**: Stores benchmark results
  - **ID**: Primary key
  - **BenchmarkName**: Name of the benchmark
  - **ModelName**: Model used
  - **ConfigID**: Reference to configuration
  - **AverageTime**, **AverageTokens**, etc.: Metrics
  - **CreatedAt**: Timestamp

## Using the Database

### Command Line Options

The application provides several database-related command line options:

```
--db PATH               Path to database file
--migrate               Migrate from file config to database
--migrate-schema        Migrate database schema to PascalCase
```

### Basic Usage

1. **First Run with Database**:
   ```
   python Main.py --db OllamaModelEditor.db
   ```
   This creates a new database if it doesn't exist and initializes all tables.

2. **Migrating from File Configuration**:
   ```
   python Main.py --db OllamaModelEditor.db --migrate
   ```
   This migrates your existing file-based configuration to the database.

3. **Migrating Database Schema**:
   ```
   python Main.py --db OllamaModelEditor.db --migrate-schema
   ```
   This migrates an existing database from snake_case to PascalCase schema.

### Migration Scripts

The application includes two migration scripts:

1. **MigrateToDatabase.py**: Migrates configuration from files to database
   ```
   python scripts/MigrateToDatabase.py --config config.yaml --db OllamaModelEditor.db
   ```

2. **MigrateDBToPascalCase.py**: Migrates database schema from snake_case to PascalCase
   ```
   python scripts/MigrateDBToPascalCase.py --db OllamaModelEditor.db --backup
   ```
   The `--backup` flag creates a backup of your database before migration.

## Benefits of the Database Approach

Using a database for configuration storage provides several advantages:

1. **Centralized Storage**: All application data in one place with a proper schema
2. **Better Organization**: Structured storage with relationships between data
3. **Improved Performance**: Faster access to configuration and history
4. **Enhanced Features**: History tracking, benchmarking, and analytics
5. **Better Multi-Model Support**: Easier to manage multiple models and configurations
6. **Simplified Backup**: Single file to back up and restore

## Backwards Compatibility

The application maintains backward compatibility with file-based configuration:

- If no database is specified, the application falls back to file-based configuration
- Configuration can be exported from the database to files
- The application can run with either approach

## For Developers

If you're developing or extending the OllamaModelEditor application, keep these points in mind:

1. **PascalCase Consistency**: All database field references should use PascalCase
2. **SQL Queries**: Ensure all SQL queries use PascalCase column names
3. **DBManager Class**: Use the `DBManager` class for all database interactions
4. **Migration Support**: Maintain support for both file and database configurations
5. **Error Handling**: Implement proper error handling for database operations

### Example Code

```python
# Correct way to interact with the database
ModelConfigs = DB.ExecuteQuery(
    """
    SELECT ModelName, ConfigName, Temperature, TopP, MaxTokens
    FROM ModelConfigs
    WHERE ModelName = ?
    """,
    (ModelName,)
)

# Correct way to update the database
DB.ExecuteNonQuery(
    """
    UPDATE ModelConfigs
    SET LastUsed = CURRENT_TIMESTAMP
    WHERE ModelName = ? AND ConfigName = ?
    """,
    (ModelName, ConfigName)
)
```

## Troubleshooting

### Common Issues

1. **Database Not Found**:
   - Check the path specified with `--db`
   - Ensure the directory exists and is writable

2. **Migration Errors**:
   - Use the `--backup` flag to create a backup before migration
   - Check logs for specific error messages
   - Restore from backup if necessary

3. **Permission Issues**:
   - Ensure you have write permissions for the database file and directory

### Database Inspection

You can inspect the database structure and content using SQLite tools:

```
sqlite3 OllamaModelEditor.db ".schema"  # Show schema
sqlite3 OllamaModelEditor.db "SELECT * FROM ModelConfigs"  # Query data
```

For a graphical interface, we recommend using [DB Browser for SQLite](https://sqlitebrowser.org/).

## Conclusion

The OllamaModelEditor database integration provides a robust foundation for managing model configurations, user preferences, and benchmarking results. By following the AIDEV-PascalCase-1.2 standard, it maintains a consistent visual fingerprint throughout the codebase while offering enhanced functionality and performance.

If you encounter any issues or have questions about the database integration, please refer to the project documentation or open an issue on the project repository.
