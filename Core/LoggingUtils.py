# File: LoggingUtils.py
# Path: OllamaModelEditor/Core/LoggingUtils.py
# Standard: AIDEV-PascalCase-1.0

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

class LoggingUtils:
    """Utilities for logging application events."""
    
    def __init__(self, log_level="INFO", log_dir=None):
        """Initialize the logging utilities.
        
        Args:
            log_level: The logging level to use
            log_dir: Optional custom log directory
        """
        self.Logger = None
        self.SetupLogger(log_level, log_dir)
    
    def SetupLogger(self, log_level="INFO", log_dir=None):
        """Set up the logger with appropriate handlers and formatting.
        
        Args:
            log_level: The logging level to use
            log_dir: Optional custom log directory
            
        Returns:
            logging.Logger: The configured logger instance
        """
        # Create logger
        self.Logger = logging.getLogger("OllamaModelEditor")
        
        # Clear any existing handlers
        if self.Logger.handlers:
            self.Logger.handlers.clear()
        
        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.Logger.setLevel(level)
        
        # Create handlers
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # File handler
        if log_dir is None:
            # Default to ~/.ollama_editor/logs directory
            log_dir = os.path.join(os.path.expanduser("~"), ".ollama_editor", "logs")
        
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(
            log_dir, 
            f"model_editor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to handlers
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.Logger.addHandler(console_handler)
        self.Logger.addHandler(file_handler)
        
        # Log initial message
        self.Logger.info(f"Logging initialized at level {log_level}")
        self.Logger.info(f"Log file: {log_file}")
        
        return self.Logger
    
    def debug(self, message):
        """Log a debug message.
        
        Args:
            message: The message to log
        """
        if self.Logger:
            self.Logger.debug(message)
    
    def info(self, message):
        """Log an info message.
        
        Args:
            message: The message to log
        """
        if self.Logger:
            self.Logger.info(message)
    
    def warning(self, message):
        """Log a warning message.
        
        Args:
            message: The message to log
        """
        if self.Logger:
            self.Logger.warning(message)
    
    def error(self, message):
        """Log an error message.
        
        Args:
            message: The message to log
        """
        if self.Logger:
            self.Logger.error(message)
    
    def critical(self, message):
        """Log a critical message.
        
        Args:
            message: The message to log
        """
        if self.Logger:
            self.Logger.critical(message)
    
    def exception(self, message):
        """Log an exception message with traceback.
        
        Args:
            message: The message to log
        """
        if self.Logger:
            self.Logger.exception(message)
    
    def get_logger(self):
        """Get the logger instance.
        
        Returns:
            logging.Logger: The logger instance
        """
        return self.Logger

# Helper function to create a logger with default settings
def SetupLogger(log_level="INFO", log_dir=None):
    """Set up and return a logger with default settings.
    
    Args:
        log_level: The logging level to use
        log_dir: Optional custom log directory
        
    Returns:
        LoggingUtils: Configured logging utilities instance
    """
    return LoggingUtils(log_level, log_dir)