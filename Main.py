# File: Main.py
# Path: OllamaModelEditor/main.py
# Standard: AIDEV-PascalCase-1.0

import sys
import os

# Add parent directory to path to enable relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from UI.MainWindow import MainWindow

def main():
    """Main entry point for the application."""
    import tkinter as tk
    
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
