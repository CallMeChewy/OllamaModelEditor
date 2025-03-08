# File: ThemeManager.py
# Path: OllamaModelEditor/UI/ThemeManager.py
# Standard: AIDEV-PascalCase-1.0

import tkinter as tk
from tkinter import ttk
import sys
import os

class ThemeManager:
    """Manages application themes (light/dark mode)."""
    
    # Theme colors
    LIGHT_THEME = {
        "bg": "#f5f5f5",
        "fg": "#333333",
        "accent": "#007bff",
        "button": "#e1e1e1",
        "highlight": "#0056b3",
        "entry": "#ffffff",
        "border": "#d1d1d1",
        "treeview": "#ffffff",
        "error": "#dc3545",
        "success": "#28a745",
        "warning": "#ffc107"
    }
    
    DARK_THEME = {
        "bg": "#2d2d2d",
        "fg": "#e0e0e0",
        "accent": "#0d6efd",
        "button": "#444444",
        "highlight": "#0a58ca",
        "entry": "#3d3d3d",
        "border": "#555555",
        "treeview": "#333333",
        "error": "#e74c3c",
        "success": "#2ecc71",
        "warning": "#f39c12"
    }
    
    def __init__(self, root, config_manager):
        """Initialize the theme manager.
        
        Args:
            root: The root tkinter window
            config_manager: The application's configuration manager
        """
        self.root = root
        self.Config = config_manager
        
        # Get theme preference from config
        self.CurrentTheme = self.Config.GetTheme() or "light"
        
        # Create styles
        self.Style = ttk.Style()
        
        # Create switch style for theme toggle
        self.Style.configure("Switch.TCheckbutton", indicatorsize=20)
        
        # Initialize theme
        self.ApplyTheme()
    
    def ApplyTheme(self, window=None):
        """Apply the current theme to the application.
        
        Args:
            window: Optional specific window to apply the theme to
        """
        target = window if window else self.root
        colors = self.DARK_THEME if self.CurrentTheme == "dark" else self.LIGHT_THEME
        
        # Configure ttk styles
        self.Style.configure("TFrame", background=colors["bg"])
        self.Style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        self.Style.configure("TButton", background=colors["button"], foreground=colors["fg"])
        self.Style.map("TButton",
            background=[("active", colors["highlight"]), ("disabled", colors["border"])],
            foreground=[("active", "#ffffff"), ("disabled", "#999999")]
        )
        self.Style.configure("TEntry", fieldbackground=colors["entry"], foreground=colors["fg"])
        self.Style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"])
        self.Style.configure("TRadiobutton", background=colors["bg"], foreground=colors["fg"])
        self.Style.configure("TCombobox", background=colors["entry"], fieldbackground=colors["entry"], foreground=colors["fg"])
        self.Style.map("TCombobox",
            fieldbackground=[("readonly", colors["entry"])],
            selectbackground=[("readonly", colors["highlight"])]
        )
        
        # Treeview styling
        self.Style.configure("Treeview", 
            background=colors["treeview"],
            foreground=colors["fg"],
            fieldbackground=colors["treeview"]
        )
        self.Style.map("Treeview",
            background=[("selected", colors["accent"])],
            foreground=[("selected", "#ffffff")]
        )
        
        # Label frames
        self.Style.configure("TLabelframe", background=colors["bg"])
        self.Style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["fg"])
        
        # Notebook styling
        self.Style.configure("TNotebook", background=colors["bg"])
        self.Style.configure("TNotebook.Tab", background=colors["button"], foreground=colors["fg"], padding=[10, 2])
        self.Style.map("TNotebook.Tab",
            background=[("selected", colors["accent"]), ("active", colors["highlight"])],
            foreground=[("selected", "#ffffff"), ("active", "#ffffff")]
        )
        
        # Scrollbar styling
        self.Style.configure("Vertical.TScrollbar", background=colors["button"], troughcolor=colors["bg"])
        self.Style.configure("Horizontal.TScrollbar", background=colors["button"], troughcolor=colors["bg"])
        
        # Switch style for theme toggle
        self.Style.map("Switch.TCheckbutton",
            indicatorcolor=[("selected", colors["accent"]), ("!selected", colors["button"])]
        )
        
        # Configure tk widgets
        target.configure(background=colors["bg"])
        
        # Apply to all tk Text widgets, Entry widgets, etc.
        self._ApplyToWidgets(target, colors)
    
    def _ApplyToWidgets(self, parent, colors):
        """Recursively apply theme to all widgets.
        
        Args:
            parent: The parent widget
            colors: The color scheme dictionary
        """
        for widget in parent.winfo_children():
            widget_type = widget.winfo_class()
            
            if widget_type == "Text":
                widget.configure(
                    background=colors["entry"],
                    foreground=colors["fg"],
                    insertbackground=colors["fg"],
                    selectbackground=colors["accent"],
                    selectforeground="#ffffff"
                )
            
            elif widget_type == "Entry":
                widget.configure(
                    background=colors["entry"],
                    foreground=colors["fg"],
                    insertbackground=colors["fg"],
                    selectbackground=colors["accent"],
                    selectforeground="#ffffff"
                )
            
            elif widget_type == "Listbox":
                widget.configure(
                    background=colors["entry"],
                    foreground=colors["fg"],
                    selectbackground=colors["accent"],
                    selectforeground="#ffffff"
                )
            
            elif widget_type == "Toplevel":
                widget.configure(background=colors["bg"])
                
            # Recursively apply to child widgets
            if widget.winfo_children():
                self._ApplyToWidgets(widget, colors)
    
    def ToggleTheme(self):
        """Toggle between light and dark theme."""
        self.CurrentTheme = "light" if self.CurrentTheme == "dark" else "dark"
        self.Config.SetTheme(self.CurrentTheme)
        self.ApplyTheme()
        
        return self.CurrentTheme
    
    def GetCurrentTheme(self):
        """Get the current theme name.
        
        Returns:
            str: The current theme name ("light" or "dark")
        """
        return self.CurrentTheme
