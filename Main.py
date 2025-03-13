# File: Main.py
# Path: OllamaModelEditor/Main.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-13 15:30PM
# Description: Entry point for the OllamaModelEditor application

import sys
import logging
import os
from pathlib import Path
import argparse
import time

# Add project root to path
ProjectRoot = Path(__file__).resolve().parent
sys.path.append(str(ProjectRoot))

# Set up basic logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
RootLogger = logging.getLogger('OllamaModelEditor')
RootLogger.info("Starting OllamaModelEditor")

def ParseCommandLine():
    """
    Parse command line arguments.
    
    Returns:
        Namespace with parsed arguments
    """
    Parser = argparse.ArgumentParser(description="OllamaModelEditor - A tool for managing Ollama AI models")
    Parser.add_argument("--config", help="Path to configuration file")
    Parser.add_argument("--db", help="Path to database file")
    Parser.add_argument("--migrate", action="store_true", help="Migrate from file config to database")
    Parser.add_argument("--migrate-schema", action="store_true", help="Migrate database schema to PascalCase")
    Parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return Parser.parse_args()

def ShowErrorAndExit(Message, Error=None):
    """
    Show error message and exit.
    
    Args:
        Message: Error message to display
        Error: Optional exception object
    """
    ErrorText = f"{Message}"
    if Error:
        ErrorText += f"\nError: {Error}"
    
    RootLogger.error(ErrorText)
    
    # Try to show GUI error message if PySide6 is available
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        App = QApplication([])
        QMessageBox.critical(None, "Error", ErrorText)
    except ImportError:
        # Fall back to console error
        print(f"ERROR: {ErrorText}")
    
    sys.exit(1)

def MigrateDBSchema(DBPath):
    """
    Migrate database schema to PascalCase.
    
    Args:
        DBPath: Path to database file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if the migration script exists
        MigrationScriptPath = str(ProjectRoot / "scripts" / "MigrateDBToPascalCase.py")
        if not os.path.exists(MigrationScriptPath):
            RootLogger.error(f"Migration script not found: {MigrationScriptPath}")
            return False
        
        # Import and run migration script
        from scripts.MigrateDBToPascalCase import MigrateDatabase
        
        # Create backup first
        BackupPath = f"{DBPath}.backup_{int(time.time())}"
        RootLogger.info(f"Creating database backup at {BackupPath}")
        
        import shutil
        shutil.copy2(DBPath, BackupPath)
        
        # Run migration
        RootLogger.info("Starting database schema migration to PascalCase...")
        Success = MigrateDatabase(DBPath)
        
        if Success:
            RootLogger.info("Database schema migration completed successfully")
            return True
        else:
            RootLogger.error("Database schema migration failed")
            return False
    except Exception as Error:
        RootLogger.error(f"Error migrating database schema: {Error}")
        return False

def Main():
    """Application entry point."""
    # Parse command line arguments
    Args = ParseCommandLine()
    
    # Set log level based on arguments
    LogLevel = logging.DEBUG if Args.debug else logging.INFO
    
    # Import Core modules
    try:
        from Core.LoggingUtils import SetupLogging
        Logger = SetupLogging(LogLevel=LogLevel, LogToFile=True)
        Logger.info("Logging initialized")
        
        from Core.DBManager import DBManager
        from Core.ConfigManager import ConfigManager
        Logger.info("Core modules imported")
    except ImportError as Error:
        ShowErrorAndExit("Failed to import Core modules", Error)
    
    # Import PySide6 components
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QSplashScreen
        from PySide6.QtCore import QTimer
        Logger.info("PySide6 modules imported")
    except ImportError as Error:
        ShowErrorAndExit("PySide6 is required but not installed.\nPlease install dependencies with: pip install -r requirements.txt", Error)
    
    # Import GUI components
    try:
        from GUI.Windows.MainWindow import MainWindow
        from GUI.Windows.SplashScreen import SplashScreen
        Logger.info("GUI modules imported")
    except ImportError as Error:
        ShowErrorAndExit("Failed to import GUI modules", Error)
    
    # Initialize database if path provided
    DBInstance = None
    if Args.db:
        try:
            # Check if schema migration is requested
            if Args.migrate_schema and os.path.exists(Args.db):
                MigrateResult = MigrateDBSchema(Args.db)
                if not MigrateResult:
                    Logger.warning("Database schema migration failed, proceeding with existing schema")
            
            # Initialize database
            DBInstance = DBManager(Args.db)
            Logger.info(f"Database initialized: {DBInstance.DBPath}")
        except Exception as Error:
            ShowErrorAndExit(f"Failed to initialize database: {Args.db}", Error)
    
    # Create application
    App = QApplication(sys.argv)
    App.setApplicationName("OllamaModelEditor")
    App.setOrganizationName("OllamaModelEditor")
    
    # Initialize configuration
    try:
        Config = ConfigManager(Args.config, DBInstance)
        
        # Migrate from file to database if requested
        if Args.migrate and DBInstance:
            try:
                Logger.info("Migrating configuration from file to database...")
                Success = Config.MigrateToDatabase(DBInstance)
                if Success:
                    Logger.info("Configuration migrated successfully")
                else:
                    Logger.warning("Configuration migration failed")
            except Exception as Error:
                Logger.error(f"Error migrating configuration: {Error}")
        
        # Load configuration
        Config.LoadConfig()
        Logger.info("Configuration loaded")
    except Exception as Error:
        ShowErrorAndExit("Failed to load configuration", Error)
    
    # Create and display splash screen
    try:
        Splash = SplashScreen()
        Splash.show()
        Logger.info("Splash screen displayed")
    except Exception as Error:
        Logger.error(f"Error creating splash screen: {Error}")
        # Continue without splash screen
        Splash = None
    
    # Initialize main window
    try:
        MainWin = MainWindow(Config)
        Logger.info("Main window created")
        
        # Close splash and show main window after delay
        if Splash:
            QTimer.singleShot(2000, lambda: ShowMainWindow(Splash, MainWin))
        else:
            MainWin.show()
    except Exception as Error:
        ShowErrorAndExit("Failed to create main window", Error)
    
    # Start event loop
    Logger.info("Starting application event loop")
    return App.exec()

def ShowMainWindow(Splash, MainWin):
    """Close splash screen and show main window."""
    try:
        Splash.finish(MainWin)
        MainWin.show()
    except Exception as Error:
        RootLogger.error(f"Error showing main window: {Error}")
        MainWin.show()

if __name__ == "__main__":
    sys.exit(Main())
