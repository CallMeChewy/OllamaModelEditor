# test_pyside.py
import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    print("Basic PySide6 imports successful")
    
    # Now try to import your custom modules
    print("Trying to import custom modules...")
    from GUI.Windows.MainWindow import MainWindow
    from GUI.Windows.SplashScreen import SplashScreen
    print("GUI modules imported successfully")
    
    from Core.LoggingUtils import SetupLogging
    from Core.ConfigManager import ConfigManager
    print("Core modules imported successfully")
    
except ImportError as e:
    print(f"Import error: {e}")