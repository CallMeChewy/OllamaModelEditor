#!/usr/bin/env python3
# File: MigrateDBToPascalCase.py
# Path: OllamaModelEditor/scripts/MigrateDBToPascalCase.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-12
# Last Modified: 2025-03-12 09:00PM
# Description: Migrates the database schema from snake_case to PascalCase

import os
import sys
import sqlite3
import json
import time
import argparse
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
Logger = logging.getLogger('DatabaseMigration')

# Add project root to path
ProjectRoot = Path(__file__).resolve().parents[1]
sys.path.append(str(ProjectRoot))

def ParseCommandLine():
    """
    Parse command line arguments.
    
    Returns:
        Namespace with parsed arguments
    """
    Parser = argparse.ArgumentParser(description="OllamaModelEditor - Database Schema Migration")
    Parser.add_argument("--db", help="Path to database file", required=True)
    Parser.add_argument("--backup", action="store_true", help="Create a backup before migration")
    Parser.add_argument("--force", action="store_true", help="Force migration even if errors occur")
    return Parser.parse_args()

def BackupDatabase(SourcePath: str) -> str:
    """
    Create a backup of the database.
    
    Args:
        SourcePath: Path to the database file
        
    Returns:
        Path to the backup file
    """
    Logger.info(f"Creating database backup...")
    
    # Define backup path
    BackupPath = f"{SourcePath}.backup_{int(time.time())}"
    
    try:
        # Connect to source database
        SourceConn = sqlite3.connect(SourcePath)
        
        # Connect to backup database
        BackupConn = sqlite3.connect(BackupPath)
        
        # Copy database content
        SourceConn.backup(BackupConn)
        
        # Close connections
        SourceConn.close()
        BackupConn.close()
        
        Logger.info(f"Database backed up to: {BackupPath}")
        return BackupPath
        
    except sqlite3.Error as Error:
        Logger.error(f"Error backing up database: {Error}")
        raise

def GetTableNames(Conn: sqlite3.Connection) -> list:
    """
    Get a list of all tables in the database.
    
    Args:
        Conn: Database connection
        
    Returns:
        List of table names
    """
    Cursor = Conn.cursor()
    Cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [Row[0] for Row in Cursor.fetchall()]

def GetColumnInfo(Conn: sqlite3.Connection, TableName: str) -> list:
    """
    Get column information for a table.
    
    Args:
        Conn: Database connection
        TableName: Name of the table
        
    Returns:
        List of column information (name, type, etc.)
    """
    Cursor = Conn.cursor()
    Cursor.execute(f"PRAGMA table_info({TableName})")
    return Cursor.fetchall()

def ConvertSnakeToPascalCase(SnakeCase: str) -> str:
    """
    Convert snake_case to PascalCase.
    
    Args:
        SnakeCase: String in snake_case
        
    Returns:
        String in PascalCase
    """
    # Special case for ID
    if SnakeCase.lower() == "id":
        return "ID"
    
    # Handle special terms
    SpecialTerms = {
        "api": "API",
        "db": "DB",
        "gui": "GUI",
        "url": "URL",
        "uri": "URI",
        "json": "JSON",
        "xml": "XML",
        "html": "HTML",
        "css": "CSS",
        "sql": "SQL"
    }
    
    # Split by underscore and convert each word
    Words = SnakeCase.split("_")
    
    # Process each word
    for i, Word in enumerate(Words):
        # Check if the word is a special term
        if Word.lower() in SpecialTerms:
            Words[i] = SpecialTerms[Word.lower()]
        else:
            # Capitalize the first letter of each word
            Words[i] = Word.capitalize()
    
    # Join words together
    return "".join(Words)

def CreateMigrationScript(SourceTables: dict) -> list:
    """
    Create SQL migration script.
    
    Args:
        SourceTables: Dictionary of table names and their columns
        
    Returns:
        List of SQL statements for migration
    """
    MigrationScript = []
    
    # Create temporary tables, copy data, drop original tables, rename temp tables
    for TableName, Columns in SourceTables.items():
        # Skip tables that already use PascalCase
        if TableName == "DBVersion" or TableName.startswith("sqlite_"):
            continue
            
        # Create PascalCase table name
        NewTableName = TableName
        if "_" in TableName:
            NewTableName = ConvertSnakeToPascalCase(TableName)
        
        # Get column definitions with PascalCase names
        ColumnDefs = []
        OldColumns = []
        NewColumns = []
        
        for Column in Columns:
            CID, Name, Type, NotNull, DefaultValue, PK = Column
            
            # Convert column name to PascalCase
            NewName = Name
            if "_" in Name:
                NewName = ConvertSnakeToPascalCase(Name)
            
            # Build column definition
            ColumnDef = f"{NewName} {Type}"
            if NotNull:
                ColumnDef += " NOT NULL"
            if DefaultValue is not None:
                ColumnDef += f" DEFAULT {DefaultValue}"
            if PK:
                ColumnDef += " PRIMARY KEY"
            
            ColumnDefs.append(ColumnDef)
            OldColumns.append(Name)
            NewColumns.append(NewName)
        
        # Create temporary table
        TempTableName = f"temp_{TableName}"
        CreateTableSQL = f"CREATE TABLE {TempTableName} ({', '.join(ColumnDefs)})"
        MigrationScript.append(CreateTableSQL)
        
        # Copy data
        OldColumnsStr = ', '.join(OldColumns)
        NewColumnsStr = ', '.join(NewColumns)
        CopyDataSQL = f"INSERT INTO {TempTableName} ({NewColumnsStr}) SELECT {OldColumnsStr} FROM {TableName}"
        MigrationScript.append(CopyDataSQL)
        
        # Drop original table
        DropTableSQL = f"DROP TABLE {TableName}"
        MigrationScript.append(DropTableSQL)
        
        # Rename temporary table
        RenameTableSQL = f"ALTER TABLE {TempTableName} RENAME TO {NewTableName}"
        MigrationScript.append(RenameTableSQL)
    
    return MigrationScript

def MigrateDatabase(DBPath: str, Force: bool = False) -> bool:
    """
    Migrate database from snake_case to PascalCase.
    
    Args:
        DBPath: Path to the database file
        Force: Whether to force migration even if errors occur
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Connect to the database
        Conn = sqlite3.connect(DBPath)
        
        # Get table names
        TableNames = GetTableNames(Conn)
        Logger.info(f"Found {len(TableNames)} tables in the database")
        
        # Get column information for each table
        SourceTables = {}
        for TableName in TableNames:
            if not TableName.startswith("sqlite_"):  # Skip SQLite internal tables
                SourceTables[TableName] = GetColumnInfo(Conn, TableName)
        
        # Create migration script
        MigrationScript = CreateMigrationScript(SourceTables)
        Logger.info(f"Generated {len(MigrationScript)} SQL statements for migration")
        
        # Execute migration script
        Cursor = Conn.cursor()
        for SQL in MigrationScript:
            try:
                Logger.debug(f"Executing: {SQL}")
                Cursor.execute(SQL)
            except sqlite3.Error as Error:
                Logger.error(f"Error executing SQL: {Error}")
                Logger.error(f"SQL: {SQL}")
                if not Force:
                    raise
        
        # Commit changes
        Conn.commit()
        Logger.info("Migration completed successfully")
        
        # Close connection
        Conn.close()
        
        return True
    
    except Exception as Error:
        Logger.error(f"Error migrating database: {Error}")
        return False

def main():
    """Main function."""
    # Parse command line arguments
    Args = ParseCommandLine()
    
    try:
        Logger.info(f"Starting database migration from snake_case to PascalCase")
        Logger.info(f"Database path: {Args.db}")
        
        # Check if database exists
        if not os.path.exists(Args.db):
            Logger.error(f"Database file not found: {Args.db}")
            return 1
        
        # Create backup if requested
        if Args.backup:
            try:
                BackupPath = BackupDatabase(Args.db)
                Logger.info(f"Backup created at: {BackupPath}")
            except Exception as Error:
                Logger.error(f"Failed to create backup: {Error}")
                return 1
        
        # Migrate database
        Success = MigrateDatabase(Args.db, Args.force)
        
        if Success:
            Logger.info("Database migration completed successfully")
            return 0
        else:
            Logger.error("Database migration failed")
            return 1
    
    except Exception as Error:
        Logger.error(f"Error: {Error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
