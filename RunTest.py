#!/usr/bin/env python3
# File: RunTest.py
# Path: OllamaModelEditor/RunTest.py
# Standard: AIDEV-PascalCase-1.0
# A simple script to test the OllamaModelEditor application with improved error reporting

import os
import sys
import traceback
import logging
import importlib.util

def SetupLogger():
    """Set up a logger for the test script."""
    Logger = logging.getLogger("TestScript")
    Logger.setLevel(logging.DEBUG)
    
    # Console handler
    ConsoleHandler = logging.StreamHandler()
    ConsoleHandler.setLevel(logging.DEBUG)
    Formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    ConsoleHandler.setFormatter(Formatter)
    Logger.addHandler(ConsoleHandler)
    
    return Logger

def CheckDependencies(Logger):
    """Check for required dependencies."""
    Logger.info("Checking dependencies...")
    
    # List of required modules
    RequiredModules = ['tkinter', 'yaml']
    MissingModules = []
    
    for Module in RequiredModules:
        try:
            importlib.import_module(Module)
            Logger.info(f"✓ {Module} is installed")
        except ImportError:
            Logger.error(f"✗ {Module} is NOT installed")
            MissingModules.append(Module)
    
    if MissingModules:
        Logger.error("Missing dependencies detected. Please install them with:")
        Logger.error(f"pip install {' '.join(MissingModules)}")
        return False
    
    return True

def CheckOllama(Logger):
    """Check if Ollama is accessible."""
    Logger.info("Checking Ollama installation...")
    
    try:
        import subprocess
        Result = subprocess.run(['ollama', 'list'], 
                               capture_output=True, 
                               text=True)
        
        if Result.returncode == 0:
            Logger.info("✓ Ollama is installed and accessible")
            
            # Count available models
            Models = [Line for Line in Result.stdout.split('\n') if Line.strip() and not Line.startswith('NAME')]
            if Models:
                Logger.info(f"✓ Found {len(Models)} Ollama models")
            else:
                Logger.warning("⚠ No Ollama models found. The application may have limited functionality.")
        else:
            Logger.error(f"✗ Ollama check failed with error: {Result.stderr}")
            return False
    except Exception as e:
        Logger.error(f"✗ Failed to check Ollama: {e}")
        return False
    
    return True

def CheckProjectStructure(Logger):
    """Check if the project structure is valid."""
    Logger.info("Checking project structure...")
    
    RequiredFiles = [
        'Main.py',
        'Core/ConfigManager.py',
        'Core/LoggingUtils.py',
        'Core/ModelManager.py',
        'Core/ParameterHandler.py',
        'UI/MainWindow.py',
        'Utils/OllamaUtils.py'
    ]
    
    AllFound = True
    for FilePath in RequiredFiles:
        if not os.path.exists(FilePath):
            Logger.error(f"✗ Required file not found: {FilePath}")
            AllFound = False
        else:
            Logger.info(f"✓ Found {FilePath}")
    
    return AllFound

def RunApplication(Logger):
    """Attempt to run the application."""
    Logger.info("Attempting to run the application...")
    
    try:
        # Add parent directory to path to enable relative imports
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Try to import the main module
        from Main import Main
        
        # Run the application
        Logger.info("Starting application. Close the window to return to the test script.")
        Main()
        
        return True
    except Exception as e:
        Logger.error(f"✗ Application failed to start: {str(e)}")
        Logger.error("Detailed traceback:")
        Logger.error(traceback.format_exc())
        return False

def Main():
    """Main function for the test script."""
    Logger = SetupLogger()
    Logger.info("Starting OllamaModelEditor test script...")
    
    # Check dependencies
    if not CheckDependencies(Logger):
        Logger.error("Dependency check failed. Please install missing dependencies.")
        return
    
    # Check Ollama
    if not CheckOllama(Logger):
        Logger.warning("Ollama check failed. The application may not work correctly.")
    
    # Check project structure
    if not CheckProjectStructure(Logger):
        Logger.error("Project structure check failed. Please ensure all required files are present.")
        return
    
    # Run the application
    Logger.info("All checks complete. Running the application...")
    Success = RunApplication(Logger)
    
    if Success:
        Logger.info("Application ran successfully!")
    else:
        Logger.error("Application failed to run correctly.")

if __name__ == "__main__":
    Main()
