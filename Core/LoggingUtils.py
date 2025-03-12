# File: LoggingUtils.py
# Path: OllamaModelEditor/Core/LoggingUtils.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Logging utilities for the OllamaModelEditor application

import logging
import os
from pathlib import Path

def SetupLogging(LogLevel=logging.INFO, LogToFile=True):
    """
    Set up logging for the application.
    
    Args:
        LogLevel: Logging level (default: INFO)
        LogToFile: Whether to log to file (default: True)
    """
    # Create logger
    Logger = logging.getLogger('OllamaModelEditor')
    Logger.setLevel(LogLevel)
    
    # Create formatter
    Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    ConsoleHandler = logging.StreamHandler()
    ConsoleHandler.setLevel(LogLevel)
    ConsoleHandler.setFormatter(Formatter)
    Logger.addHandler(ConsoleHandler)
    
    # Create file handler if requested
    if LogToFile:
        # Determine log directory
        HomeDir = Path.home()
        if os.name == 'nt':  # Windows
            LogDir = HomeDir / 'AppData' / 'Local' / 'OllamaModelEditor' / 'logs'
        else:  # macOS and Linux
            LogDir = HomeDir / '.config' / 'ollamaModelEditor' / 'logs'
        
        # Create directory if it doesn't exist
        LogDir.mkdir(parents=True, exist_ok=True)
        
        # Create file handler
        LogFile = LogDir / 'ollamaModelEditor.log'
        FileHandler = logging.FileHandler(str(LogFile))
        FileHandler.setLevel(LogLevel)
        FileHandler.setFormatter(Formatter)
        Logger.addHandler(FileHandler)
    
    return Logger
