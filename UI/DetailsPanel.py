# File: DetailsPanel.py
# Path: OllamaModelEditor/UI/DetailsPanel.py
# Standard: AIDEV-PascalCase-1.0

import tkinter as tk
from tkinter import ttk

class DetailsPanel:
    """Panel for displaying model details."""
    
    def __init__(self, parent):
        """Initialize the details panel.
        
        Args:
            parent: Parent frame
        """
        self.Parent = parent
        self.DetailValues = {}
        
        # Create panel
        self.Frame = ttk.LabelFrame(parent, text="Model Details", padding="5")
        self.Frame.pack(fill=tk.X, pady=5)
        
        # Create grid for model details
        details_grid = ttk.Frame(self.Frame)
        details_grid.pack(fill=tk.X, expand=True)
        
        # Create labels for model details
        detail_labels = ["Architecture", "Parameters", "Context Length", "Embedding Length", "Quantization", "License"]
        
        for i, label in enumerate(detail_labels):
            row = i // 3
            col = i % 3 * 2
            
            ttk.Label(details_grid, text=f"{label}:", width=15).grid(row=row, column=col, padx=5, pady=2, sticky=tk.W)
            value_var = tk.StringVar(value="-")
            ttk.Label(details_grid, textvariable=value_var, width=15).grid(row=row, column=col+1, padx=5, pady=2, sticky=tk.W)
            self.DetailValues[label.lower().replace(" ", "_")] = value_var
    
    def UpdateModelDetails(self, details):
        """Update the displayed model details.
        
        Args:
            details: Dictionary containing model details
        """
        # Map the details to the display variables
        mappings = {
            "architecture": "architecture",
            "parameters": "parameters",
            "context_length": "context_length",
            "embedding_length": "embedding_length",
            "quantization": "quantization",
            "license": "license"
        }
        
        # Update each value
        for display_key, detail_key in mappings.items():
            if display_key in self.DetailValues:
                value = details.get(detail_key, "-")
                self.DetailValues[display_key].set(value)
    
    def Clear(self):
        """Clear all displayed details."""
        for var in self.DetailValues.values():
            var.set("-")
