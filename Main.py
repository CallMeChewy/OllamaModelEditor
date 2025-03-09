# File: Main.py
# Path: OllamaModelEditor/Main.py
# Standard: AIDEV-PascalCase-1.0

import sys
import os

# Add parent directory to path to enable relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from UI.MainWindow import MainWindow

def Main():
    """Main entry point for the application."""
    import tkinter as tk
    
    Root = tk.Tk()
    App = MainWindow(Root)
    Root.mainloop()

if __name__ == "__main__":
    Main()
