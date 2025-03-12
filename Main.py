# File: Main.py
# Path: OllamaModelEditor/Main.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Entry point for the OllamaModelEditor application

import sys
from pathlib import Path

# Add project root to path
ProjectRoot = Path(__file__).resolve().parent
sys.path.append(str(ProjectRoot))

# Import GUI components
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    from GUI.Windows.MainWindow import MainWindow
    from GUI.Windows.SplashScreen import SplashScreen
except ImportError:
    print("Error: PySide6 is required but not installed.")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)

# Import core components
from Core.LoggingUtils import SetupLogging
from Core.ConfigManager import ConfigManager

def Main():
    """Application entry point."""
    # Initialize logging
    SetupLogging()
    
    # Create application
    App = QApplication(sys.argv)
    App.setApplicationName("OllamaModelEditor")
    App.setOrganizationName("CallMeChewy")
    
    # Initialize configuration
    Config = ConfigManager()
    Config.LoadConfig()
    
    # Create and display splash screen
    Splash = SplashScreen()
    Splash.show()
    
    # Initialize main window
    MainWin = MainWindow(Config)
    
    # Close splash and show main window after delay
    QTimer.singleShot(2000, lambda: ShowMainWindow(Splash, MainWin))
    
    # Start event loop
    return App.exec()

def ShowMainWindow(Splash, MainWin):
    """Close splash screen and show main window."""
    Splash.finish(MainWin)
    MainWin.show()

if __name__ == "__main__":
    sys.exit(Main())
