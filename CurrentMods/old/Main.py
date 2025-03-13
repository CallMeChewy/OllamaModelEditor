# File: Main.py
# Path: OllamaModelEditor/Main.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-13
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
    from Core.ParameterStateManager import ParameterStateManager
    Logger.info("Core modules imported")
except ImportError as e:
    Logger.error(f"Error importing Core components: {e}")
    print(f"Error importing Core components: {e}")
    print("Please make sure all required files are in place.")
    sys.exit(1)

# Import PySide6 components
try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
    from PySide6.QtCore import QTimer
    Logger.info("PySide6 modules imported")
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

def ShowErrorAndExit(Message, Error=None):
    """
    Show error message and exit application.
    
    Args:
        Message: Error message to display
        Error: Optional error object with details
    """
    Logger.error(f"{Message}")
    if Error:
        Logger.error(f"Error: {Error}")
    
    # Create QApplication if needed
    App = QApplication([])
    
    # Show error message
    QMessageBox.critical(None, "OllamaModelEditor Error", f"{Message}\n\n{Error}")
    
    # Exit application
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
    try:
        DB = DBManager(Args.db) if Args.db else None
        if DB:
            Logger.info(f"Database initialized: {DB.DBPath}")
    except Exception as Error:
        ShowErrorAndExit("Error initializing database", Error)
    
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
    except Exception as Error:
        ShowErrorAndExit("Error loading configuration", Error)
    
    # Create and display splash screen
    try:
        Splash = SplashScreen()
        Splash.show()
        Logger.info("Splash screen displayed")
    except Exception as Error:
        Logger.error(f"Error creating splash screen: {Error}")
        # Continue without splash screen
        Splash = None
    
    # Create model manager
    try:
        from Core.ModelManager import ModelManager
        ModelManager = ModelManager(Config)
    except Exception as Error:
        ShowErrorAndExit("Error creating model manager", Error)
    
    # Create parameter state manager
    try:
        StateManager = ParameterStateManager(ModelManager, Config)
    except Exception as Error:
        ShowErrorAndExit("Error creating parameter state manager", Error)
    
    # Initialize main window
    try:
        # Update this line to pass StateManager to MainWindow
        MainWin = MainWindow(Config, StateManager)
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
        Logger.error(f"Error showing main window: {Error}")
        MainWin.show()

if __name__ == "__main__":
    sys.exit(Main())
