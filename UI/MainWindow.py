# File: MainWindow.py
# Path: OllamaModelEditor/UI/MainWindow.py
# Standard: AIDEV-PascalCase-1.0

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path to enable relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UI.ParameterPanel import ParameterPanel
from UI.DetailsPanel import DetailsPanel
from UI.ComparisonTool import ComparisonTool
from UI.ThemeManager import ThemeManager
from Core.ModelManager import ModelManager
from Core.ConfigManager import ConfigManager
from Core.LoggingUtils import SetupLogger
from Utils.OllamaUtils import OllamaInterface

class MainWindow:
    """Main application window for Ollama Model Editor."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.Root = root
        self.Root.title("Ollama Model Editor")
        self.Root.geometry("1200x900")
        
        # Initialize core components
        self.Config = ConfigManager()
        self.Logger = SetupLogger()
        self.OllamaUtils = OllamaInterface()
        self.ModelManager = ModelManager(self.OllamaUtils, self.Logger)
        
        # Initialize theme manager
        self.ThemeManager = ThemeManager(self.Root, self.Config)
        
        # Data storage
        self.CurrentModel = None
        
        # Create main layout
        self.CreateMainLayout()
        
        # Bind closing event to cleanup
        self.Root.protocol("WM_DELETE_WINDOW", self.OnClose)
        
        # Log application start
        self.Logger.info("Application started")
    
    def CreateMainLayout(self):
        """Create the main application layout."""
        # Create main frame with padding
        MainFrame = ttk.Frame(self.Root, padding="10")
        MainFrame.pack(fill=tk.BOTH, expand=True)
        
        # Top section - Model selection
        ModelFrame = ttk.LabelFrame(MainFrame, text="Model Selection", padding="5")
        ModelFrame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ModelFrame, text="Select model:").pack(side=tk.LEFT, padx=5)
        self.ModelCombo = ttk.Combobox(ModelFrame, width=40, state="readonly")
        self.ModelCombo.pack(side=tk.LEFT, padx=5)
        self.ModelCombo.bind("<<ComboboxSelected>>", self.OnModelSelected)
        
        ttk.Button(ModelFrame, text="Refresh Models", command=self.FetchModels).pack(side=tk.LEFT, padx=5)
        
        # Theme toggle
        self.ThemeToggle = ttk.Checkbutton(
            ModelFrame, 
            text="Dark Mode",
            command=self.ToggleTheme,
            style='Switch.TCheckbutton'
        )
        self.ThemeToggle.pack(side=tk.RIGHT, padx=5)
        
        # Model details section
        self.DetailsPanel = DetailsPanel(MainFrame)
        
        # Middle section - Parameter grid and info
        MiddleFrame = ttk.Frame(MainFrame)
        MiddleFrame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Parameters panel
        self.ParameterPanel = ParameterPanel(
            MiddleFrame, 
            self.ModelManager, 
            self.Config,
            self.Logger
        )
        
        # Bottom section - New model name and action buttons
        BottomFrame = ttk.LabelFrame(MainFrame, text="Create New Model", padding="5")
        BottomFrame.pack(fill=tk.X, pady=5)
        
        ttk.Label(BottomFrame, text="New model name:").pack(side=tk.LEFT, padx=5)
        self.NewModelName = ttk.Entry(BottomFrame, width=30)
        self.NewModelName.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(BottomFrame, text="Create Model", command=self.CreateModel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(BottomFrame, text="Cancel", command=self.ResetForm).pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.StatusVar = tk.StringVar()
        self.StatusVar.set("Ready")
        StatusBar = ttk.Label(MainFrame, textvariable=self.StatusVar, relief=tk.SUNKEN, anchor=tk.W)
        StatusBar.pack(fill=tk.X, pady=(5, 0))
        
        # Additional features
        ButtonFrame = ttk.Frame(MainFrame)
        ButtonFrame.pack(fill=tk.X, pady=5)
        
        ttk.Button(ButtonFrame, text="View Model History", command=self.ViewModelHistory).pack(side=tk.LEFT, padx=5)
        ttk.Button(ButtonFrame, text="View Modelfile", command=self.ViewModelfile).pack(side=tk.LEFT, padx=5)
        ttk.Button(ButtonFrame, text="Export Configuration", command=self.ExportConfig).pack(side=tk.LEFT, padx=5)
        ttk.Button(ButtonFrame, text="Import Configuration", command=self.ImportConfig).pack(side=tk.LEFT, padx=5)
        ttk.Button(ButtonFrame, text="Compare Models", command=self.CompareModels).pack(side=tk.LEFT, padx=5)
        ttk.Button(ButtonFrame, text="AI Advisor", command=self.OpenAIAdvisor).pack(side=tk.LEFT, padx=5)
    
    def FetchModels(self):
        """Fetch available Ollama models."""
        try:
            self.StatusVar.set("Fetching models...")
            self.Root.update_idletasks()
            
            Models = self.ModelManager.GetModelList()
            
            self.ModelCombo["values"] = Models
            
            if Models:
                if self.CurrentModel and self.CurrentModel in Models:
                    self.ModelCombo.set(self.CurrentModel)
                else:
                    self.ModelCombo.current(0)
                    self.OnModelSelected(None)
            
            self.StatusVar.set(f"Found {len(Models)} models")
            
        except Exception as e:
            self.StatusVar.set("Error fetching models")
            self.Logger.error(f"Error fetching models: {e}")
            messagebox.showerror("Error", f"Failed to fetch models: {e}")
    
    def OnModelSelected(self, event):
        """Handle model selection event."""
        ModelName = self.ModelCombo.get()
        if not ModelName:
            return
        
        self.CurrentModel = ModelName
        self.StatusVar.set(f"Loading model: {ModelName}")
        self.Root.update_idletasks()
        
        try:
            # Get model details and parameters
            ModelDetails = self.ModelManager.GetModelDetails(ModelName)
            Parameters = self.ModelManager.GetModelParameters(ModelName)
            
            # Update UI components
            self.DetailsPanel.UpdateModelDetails(ModelDetails)
            self.ParameterPanel.UpdateParameters(Parameters)
            
            # Suggest new model name
            self.NewModelName.delete(0, tk.END)
            self.NewModelName.insert(0, f"{ModelName}-custom")
            
            self.StatusVar.set(f"Model {ModelName} loaded")
            
        except Exception as e:
            self.StatusVar.set(f"Error loading model {ModelName}")
            self.Logger.error(f"Error loading model {ModelName}: {e}")
            messagebox.showerror("Error", f"Failed to load model {ModelName}: {e}")
    
    def CreateModel(self):
        """Create a new model with the specified parameters."""
        if not self.CurrentModel:
            messagebox.showerror("Error", "No model selected")
            return
        
        NewName = self.NewModelName.get().strip()
        if not NewName:
            messagebox.showerror("Error", "Please enter a name for the new model")
            self.NewModelName.focus_set()
            return
        
        # Get changed parameters from parameter panel
        ChangedParams = self.ParameterPanel.GetChangedParameters()
        
        if not ChangedParams:
            messagebox.showinfo("No Changes", "No parameters have been changed")
            return
        
        try:
            # Create the model
            self.StatusVar.set(f"Creating model {NewName}...")
            self.Root.update_idletasks()
            
            self.ModelManager.CreateModel(NewName, self.CurrentModel, ChangedParams)
            
            # Update model list
            self.FetchModels()
            
            # Select the new model
            if NewName in self.ModelCombo["values"]:
                self.ModelCombo.set(NewName)
                self.OnModelSelected(None)
            
            self.StatusVar.set(f"Model {NewName} created successfully")
            messagebox.showinfo("Success", f"Model {NewName} created successfully")
            
        except Exception as e:
            self.StatusVar.set(f"Error creating model")
            self.Logger.error(f"Error creating model {NewName}: {e}")
            messagebox.showerror("Error", f"Failed to create model: {e}")
    
    def ResetForm(self):
        """Reset the form to its initial state."""
        self.ParameterPanel.ResetChanges()
        
        # Reset new model name
        if self.CurrentModel:
            self.NewModelName.delete(0, tk.END)
            self.NewModelName.insert(0, f"{self.CurrentModel}-custom")
        
        self.StatusVar.set("Form reset")
    
    def ViewModelHistory(self):
        """View the model creation history."""
        messagebox.showinfo("Info", "Model history feature will be implemented in a future update.")
    
    def ViewModelfile(self):
        """View the Modelfile of the current model."""
        if not self.CurrentModel:
            messagebox.showerror("Error", "No model selected")
            return
        
        try:
            Modelfile = self.ModelManager.GetModelfile(self.CurrentModel)
            
            # Create a new window to display the Modelfile
            ModelfileWindow = tk.Toplevel(self.Root)
            ModelfileWindow.title(f"Modelfile: {self.CurrentModel}")
            ModelfileWindow.geometry("800x600")
            
            # Set theme
            self.ThemeManager.ApplyTheme(ModelfileWindow)
            
            # Create a text widget to display the Modelfile
            TextWidget = tk.Text(ModelfileWindow, wrap=tk.WORD)
            TextWidget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            TextWidget.insert(tk.END, Modelfile)
            TextWidget.config(state=tk.DISABLED)
            
            # Add scrollbar
            Scrollbar = ttk.Scrollbar(TextWidget, command=TextWidget.yview)
            TextWidget.configure(yscrollcommand=Scrollbar.set)
            Scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        except Exception as e:
            self.Logger.error(f"Error viewing Modelfile: {e}")
            messagebox.showerror("Error", f"Failed to view Modelfile: {e}")
    
    def ExportConfig(self):
        """Export the current configuration to a file."""
        messagebox.showinfo("Info", "Export feature will be implemented in a future update.")
    
    def ImportConfig(self):
        """Import a configuration from a file."""
        messagebox.showinfo("Info", "Import feature will be implemented in a future update.")
    
    def CompareModels(self):
        """Compare parameters between different models."""
        ComparisonTool = ComparisonTool(self.Root, self.ModelManager, self.ThemeManager)
        ComparisonTool.Show()
    
    def OpenAIAdvisor(self):
        """Open the AI advisor for parameter suggestions."""
        messagebox.showinfo("Info", "AI Advisor feature will be implemented in a future update.")
    
    def ToggleTheme(self):
        """Toggle between light and dark theme."""
        self.ThemeManager.ToggleTheme()
    
    def OnClose(self):
        """Handle application close event."""
        # Save current state to config
        if self.CurrentModel:
            self.Config.SetLastModel(self.CurrentModel)
        
        self.Config.SaveConfig()
        self.Logger.info("Application closed")
        self.Root.destroy()
