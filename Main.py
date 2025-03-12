# File: Main.py
# Path: OllamaModelEditor/Main.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-12 05:45PM
# Description: Entry point for the OllamaModelEditor application

import sys
import logging
from pathlib import Path
import argparse

# Add project root to path
ProjectRoot = Path(__file__).resolve().parent
sys.path.append(str(ProjectRoot))

# Set up basic logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
Logger = logging.getLogger('OllamaModelEditor')

# Import Core components first to ensure they're available
try:
    from Core.DBManager import DBManager
    from Core.LoggingUtils import SetupLogging
    from Core.ConfigManager import ConfigManager
    Logger.info("Core imports successful")
except ImportError as e:
    Logger.error(f"Error importing Core components: {e}")
    print(f"Error importing Core components: {e}")
    print("Please make sure all required files are in place.")
    sys.exit(1)

# Import PySide6 components
try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
    from PySide6.QtCore import QTimer
    Logger.info("PySide6 imports successful")
except ImportError as e:
    Logger.error(f"Error importing PySide6: {e}")
    print("Error: PySide6 is required but not installed.")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)

# Import GUI components
try:
    from GUI.Windows.MainWindow import MainWindow
    from GUI.Windows.SplashScreen import SplashScreen
    Logger.info("GUI imports successful")
except ImportError as e:
    Logger.error(f"Error importing GUI components: {e}")
    print(f"Error importing GUI components: {e}")
    print("Please make sure all required files are in place.")
    sys.exit(1)

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
    Parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return Parser.parse_args()

def Main():
    """Application entry point."""
    # Parse command line arguments
    Args = ParseCommandLine()
    
    # Set log level based on arguments
    LogLevel = logging.DEBUG if Args.debug else logging.INFO
    
    Logger.info("Starting OllamaModelEditor")
    
    # Initialize database if using database storage
    DB = DBManager(Args.db) if DBManager else None
    Logger.info(f"Database initialized: {DB.DBPath if DB else 'Not using database'}")
    
    # Initialize logging
    SetupLogging(LogLevel=LogLevel)
    
    # Create application
    App = QApplication(sys.argv)
    App.setApplicationName("OllamaModelEditor")
    App.setOrganizationName("CallMeChewy")
    
    # Initialize configuration
    try:
        Config = ConfigManager(Args.config, DB)
        
        # Migrate from file to database if requested
        if Args.migrate and DB:
            Config.MigrateToDatabase(DB)
        
        Config.LoadConfig()
        Logger.info("Configuration loaded")
    except Exception as e:
        Logger.error(f"Error loading configuration: {e}")
        QMessageBox.critical(None, "Configuration Error", 
                            f"Error loading configuration: {e}")
        return 1
    
    # Create and display splash screen
    try:
        Splash = SplashScreen()
        Splash.show()
        Logger.info("Splash screen displayed")
    except Exception as e:
        Logger.error(f"Error creating splash screen: {e}")
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
    except Exception as e:
        Logger.error(f"Error creating main window: {e}")
        QMessageBox.critical(None, "Error", 
                            f"Error creating main window: {e}")
        return 1
    
    # Start event loop
    Logger.info("Starting application event loop")
    return App.exec()

def ShowMainWindow(Splash, MainWin):
    """Close splash screen and show main window."""
    try:
        Splash.finish(MainWin)
        MainWin.show()
    except Exception as e:
        Logger.error(f"Error showing main window: {e}")
        MainWin.show()

if __name__ == "__main__":
    sys.exit(Main())
