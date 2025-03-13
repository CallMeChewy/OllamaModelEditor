# Database Migration to PascalCase Standard

## Overview

As part of our commitment to the AIDEV-PascalCase-1.2 standard, we've updated our database schema to use PascalCase for all table and column names. This document explains why this change was made and provides instructions for migrating existing databases to the new standard.

## Why PascalCase for Database Schema?

The AIDEV-PascalCase standard specifies that PascalCase should be used for naming conventions across the entire codebase, including:

- Classes
- Methods
- Functions
- Variables
- Database elements (tables, columns, etc.)

By using PascalCase for all database elements, we maintain a consistent visual fingerprint throughout the codebase. This consistency:

1. Improves code readability
2. Eliminates the need for mental translation between snake_case and PascalCase
3. Strengthens the distinctive signature of the project
4. Makes it easier to identify and correct naming inconsistencies

## Key Changes

The following changes have been made to standardize the database schema:

1. All table names now use PascalCase (e.g., `model_configs` → `ModelConfigs`)
2. All column names now use PascalCase (e.g., `model_name` → `ModelName`)
3. Special terms are properly capitalized (e.g., `api_key` → `APIKey`, `db_connection` → `DBConnection`)
4. Database filename uses PascalCase (`OllamaModelEditor.db` instead of `ollama_model_editor.db`)
5. Related file paths also use PascalCase for consistency

## Migration Process

### Automatic Migration

We provide a migration script that will automatically convert your existing database to the new PascalCase standard:

```bash
python scripts/MigrateDBToPascalCase.py --db /path/to/your/database.db --backup
```

The `--backup` flag will create a backup of your database before migration, which is strongly recommended.

### Migration Process Details

The migration script will:

1. Create a backup of your database (if the `--backup` flag is used)
2. Analyze all tables and columns in the database
3. Create temporary tables with PascalCase names and column definitions
4. Copy data from the original tables to the temporary tables
5. Drop the original tables
6. Rename the temporary tables to their final PascalCase names

### Manual Migration

If you prefer to perform the migration manually or if the automatic migration fails, you can use the SQL schema file `Core/DatabaseSchema.sql` to create a new database with the PascalCase standard, and then manually copy your data:

```bash
# Create a new database with the PascalCase schema
sqlite3 OllamaModelEditor_new.db < Core/DatabaseSchema.sql

# Then use SQLite tools to export and import your data
```

## Troubleshooting

If you encounter any issues during migration:

1. Check the logs for specific error messages
2. Restore from the backup if available
3. Try using the `--force` flag with the migration script to continue despite non-critical errors
4. If all else fails, create a new database using the schema file and manually copy your data

## Verifying Migration Success

After migration, you can verify that the database structure has been properly updated:

```bash
sqlite3 OllamaModelEditor.db ".schema"
```

All table and column names should now use PascalCase, with special terms like "API", "DB", etc. properly capitalized.

## Moving Forward

From this point forward, all database operations will use the PascalCase naming convention. The `DBManager` class has been updated to work with the new schema, so all database operations should continue to work seamlessly after migration.

## Support

If you encounter any issues with the migration process or the new database schema, please open an issue on the project repository or contact the project maintainer at Herb@BowersWorld.com.
