# File: ParameterPanel.py
# Path: OllamaModelEditor/UI/ParameterPanel.py
# Standard: AIDEV-PascalCase-1.0

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from typing import Dict, List, Any, Optional

# Import parameter handler for documentation and validation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Core.ParameterHandler import ParameterHandler

class ParameterPanel:
    """Panel for displaying and editing model parameters."""
    
    def __init__(self, parent, model_manager, config_manager, logger):
        """Initialize the parameter panel.
        
        Args:
            parent: Parent frame
            model_manager: The model manager instance
            config_manager: The configuration manager instance
            logger: The logger instance
        """
        self.Parent = parent
        self.ModelManager = model_manager
        self.Config = config_manager
        self.Logger = logger
        
        # Initialize parameter handler
        self.ParameterHandler = ParameterHandler(self.Config, self.Logger)
        
        # Data storage
        self.OriginalParams = {}
        self.ParameterWidgets = {}
        self.MultiValueParams = {}
        
        # Create panel
        self.CreatePanel()
    
    def CreatePanel(self):
        """Create the parameter panel layout."""
        # Create the frame with two sections: parameters and info
        
        # Parameters grid (left side)
        self.ParamFrame = ttk.LabelFrame(self.Parent, text="Parameters", padding="5")
        self.ParamFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Create scrollable frame for parameters
        ParamCanvas = tk.Canvas(self.ParamFrame)
        Scrollbar = ttk.Scrollbar(self.ParamFrame, orient="vertical", command=ParamCanvas.yview)
        self.ScrollableFrame = ttk.Frame(ParamCanvas)
        
        self.ScrollableFrame.bind(
            "<Configure>",
            lambda e: ParamCanvas.configure(scrollregion=ParamCanvas.bbox("all"))
        )
        
        ParamCanvas.create_window((0, 0), window=self.ScrollableFrame, anchor="nw")
        ParamCanvas.configure(yscrollcommand=Scrollbar.set)
        
        ParamCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        Scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create header row for parameters
        HeaderFrame = ttk.Frame(self.ScrollableFrame)
        HeaderFrame.pack(fill=tk.X)
        
        ttk.Label(HeaderFrame, text="Parameter", width=15).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(HeaderFrame, text="Original Value", width=15).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(HeaderFrame, text="Changed Value", width=15).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(HeaderFrame, text="Actions", width=10).grid(row=0, column=3, padx=5, pady=5)
        
        # Parameter info (right side)
        self.InfoFrame = ttk.LabelFrame(self.Parent, text="Parameter Info", padding="5")
        self.InfoFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.InfoText = tk.Text(self.InfoFrame, wrap=tk.WORD, width=40, height=10)
        self.InfoText.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar to info text
        InfoScrollbar = ttk.Scrollbar(self.InfoText, orient="vertical", command=self.InfoText.yview)
        self.InfoText.configure(yscrollcommand=InfoScrollbar.set)
        InfoScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.InfoText.config(state=tk.DISABLED)
    
    def UpdateParameters(self, parameters):
        """Update the displayed parameters.
        
        Args:
            parameters: Dictionary of parameters
        """
        # Store original parameters
        self.OriginalParams = parameters
        
        # Clear existing parameter widgets
        for widget in self.ScrollableFrame.winfo_children():
            if widget != self.ScrollableFrame.winfo_children()[0]:  # Preserve header
                widget.destroy()
        
        self.ParameterWidgets = {}
        self.MultiValueParams = {}
        
        # Process multi-value parameters
        for ParamName, Value in parameters.items():
            if isinstance(Value, list):
                self.MultiValueParams[ParamName] = Value
        
        # Create parameter grid
        Row = 1
        ParamList = self.ParameterHandler.GetParameterNames()
        
        for ParamName in sorted(ParamList):
            Frame = ttk.Frame(self.ScrollableFrame)
            Frame.pack(fill=tk.X)
            
            # Parameter name
            ttk.Label(Frame, text=ParamName, width=15).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
            
            # Original value
            if ParamName in self.MultiValueParams:
                # For multi-value parameters, join values with a separator
                OriginalValue = "; ".join(self.MultiValueParams[ParamName])
            else:
                OriginalValue = parameters.get(ParamName, "")
            
            OriginalEntry = ttk.Entry(Frame, width=15)
            OriginalEntry.grid(row=0, column=1, padx=5, pady=2)
            OriginalEntry.insert(0, OriginalValue)
            OriginalEntry.config(state="readonly")
            
            # Changed value
            ChangedEntry = ttk.Entry(Frame, width=15)
            ChangedEntry.grid(row=0, column=2, padx=5, pady=2)
            
            # Action buttons for multi-value parameters
            ActionFrame = ttk.Frame(Frame)
            ActionFrame.grid(row=0, column=3, padx=5, pady=2)
            
            # If parameter has options, create a dropdown instead
            ParamInfo = self.ParameterHandler.GetParameterInfo(ParamName)
            if ParamInfo and "options" in ParamInfo:
                ChangedEntry.grid_forget()  # Remove entry widget
                Options = [str(opt) for opt in ParamInfo["options"]]
                ChangedCombo = ttk.Combobox(Frame, values=Options, width=15)
                ChangedCombo.grid(row=0, column=2, padx=5, pady=2)
                if OriginalValue and OriginalValue in Options:
                    ChangedCombo.set(OriginalValue)
                self.ParameterWidgets[ParamName] = {
                    "original": OriginalEntry,
                    "changed": ChangedCombo,
                    "type": "combo",
                    "action_frame": ActionFrame
                }
                # Bind click event to show info
                ChangedCombo.bind("<FocusIn>", lambda e, pn=ParamName: self.ShowParamInfo(pn))
            else:
                self.ParameterWidgets[ParamName] = {
                    "original": OriginalEntry,
                    "changed": ChangedEntry,
                    "type": "entry",
                    "action_frame": ActionFrame
                }
                # Add key bindings
                ChangedEntry.bind("<FocusIn>", lambda e, pn=ParamName: self.ShowParamInfo(pn))
                ChangedEntry.bind("<KeyPress>", self.HandleKeyPress)
            
            # Add special handling for multi-value parameters
            if ParamInfo and ParamInfo.get("multi_value", False):
                AddBtn = ttk.Button(
                    ActionFrame, 
                    text="+", 
                    width=2,
                    command=lambda pn=ParamName: self.AddMultiValue(pn)
                )
                AddBtn.pack(side=tk.LEFT, padx=2)
                
                ViewBtn = ttk.Button(
                    ActionFrame, 
                    text="...", 
                    width=2,
                    command=lambda pn=ParamName: self.ViewMultiValues(pn)
                )
                ViewBtn.pack(side=tk.LEFT, padx=2)
            
            Row += 1
        
        # Show parameter info for the first parameter if available
        if ParamList:
            self.ShowParamInfo(ParamList[0])
    
    def ShowParamInfo(self, param_name):
        """Show information about the selected parameter.
        
        Args:
            param_name: The parameter name
        """
        ParamInfo = self.ParameterHandler.GetParameterInfo(param_name)
        
        if not ParamInfo:
            return
        
        # Get parameter documentation display settings
        DocSettings = self.Config.GetParameterDocsSettings()
        
        # Format the information text
        InfoText = f"Parameter: {param_name}\n\n"
        InfoText += f"Description: {ParamInfo.get('description', 'No description available')}\n\n"
        InfoText += f"Type: {ParamInfo.get('type', 'Unknown')}\n\n"
        
        if "options" in ParamInfo:
            InfoText += f"Valid options: {', '.join(str(opt) for opt in ParamInfo['options'])}\n\n"
        elif "min" in ParamInfo and "max" in ParamInfo:
            InfoText += f"Valid range: {ParamInfo['min']} to {ParamInfo['max']}\n\n"
        
        InfoText += f"Default: {ParamInfo.get('default', 'Not specified')}\n\n"
        InfoText += f"Help: {ParamInfo.get('help', 'No help available')}\n\n"
        
        # Add cautions if enabled
        if DocSettings.get("ShowCautions", True) and "caution" in ParamInfo:
            InfoText += f"⚠️ Caution: {ParamInfo['caution']}\n\n"
        
        # Add examples if enabled
        if DocSettings.get("ShowExamples", True) and "examples" in ParamInfo:
            InfoText += "Examples:\n"
            for Example in ParamInfo["examples"]:
                InfoText += f"• {Example}\n"
            InfoText += "\n"
        
        # Add performance impact if enabled
        if DocSettings.get("ShowPerformanceImpact", True) and "performance_impact" in ParamInfo:
            InfoText += f"Performance Impact: {ParamInfo['performance_impact']}\n\n"
        
        # Update the info text
        self.InfoText.config(state=tk.NORMAL)
        self.InfoText.delete(1.0, tk.END)
        self.InfoText.insert(tk.END, InfoText)
        self.InfoText.config(state=tk.DISABLED)
    
    def HandleKeyPress(self, event):
        """Handle key presses in the parameter entry fields.
        
        Args:
            event: The key event
        """
        if event.char == "." and event.widget in [widgets["changed"] for widgets in self.ParameterWidgets.values() if widgets["type"] == "entry"]:
            # Find which parameter this is
            for ParamName, Widgets in self.ParameterWidgets.items():
                if Widgets["changed"] == event.widget:
                    # Copy value from original
                    OriginalValue = Widgets["original"].get()
                    event.widget.delete(0, tk.END)
                    event.widget.insert(0, OriginalValue)
                    return "break"  # Prevent default behavior
    
    def AddMultiValue(self, param_name):
        """Add an additional value for a multi-value parameter.
        
        Args:
            param_name: The parameter name
        """
        if param_name not in self.ParameterWidgets:
            return
        
        # Create dialog to enter new value
        Dialog = tk.Toplevel(self.Parent)
        Dialog.title(f"Add Value for {param_name}")
        Dialog.geometry("400x150")
        Dialog.transient(self.Parent.winfo_toplevel())
        Dialog.grab_set()
        
        # Center dialog on parent window
        ParentRoot = self.Parent.winfo_toplevel()
        X = ParentRoot.winfo_x() + (ParentRoot.winfo_width() - 400) // 2
        Y = ParentRoot.winfo_y() + (ParentRoot.winfo_height() - 150) // 2
        Dialog.geometry(f"+{X}+{Y}")
        
        # Create frame for content
        Frame = ttk.Frame(Dialog, padding="10")
        Frame.pack(fill=tk.BOTH, expand=True)
        
        # Add label and entry
        ttk.Label(Frame, text=f"Enter value for {param_name}:").pack(pady=(0, 5))
        EntryWidget = ttk.Entry(Frame, width=40)
        EntryWidget.pack(pady=5, fill=tk.X)
        EntryWidget.focus_set()
        
        # Add buttons
        ButtonFrame = ttk.Frame(Frame)
        ButtonFrame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            ButtonFrame, 
            text="Add", 
            command=lambda: self.AddMultiValueCallback(Dialog, param_name, EntryWidget.get())
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            ButtonFrame, 
            text="Cancel", 
            command=Dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Handle Enter key
        EntryWidget.bind("<Return>", lambda e: self.AddMultiValueCallback(Dialog, param_name, EntryWidget.get()))
    
    def AddMultiValueCallback(self, dialog, param_name, value):
        """Callback for adding a multi-value parameter.
        
        Args:
            dialog: The dialog window
            param_name: The parameter name
            value: The value to add
        """
        if not value.strip():
            messagebox.showerror("Error", "Please enter a value", parent=dialog)
            return
        
        # Update the multi_value_params dictionary
        if param_name not in self.MultiValueParams:
            CurrentValue = self.OriginalParams.get(param_name, "")
            self.MultiValueParams[param_name] = [CurrentValue] if CurrentValue else []
        
        self.MultiValueParams[param_name].append(value)
        
        # Update the original value display
        Widgets = self.ParameterWidgets[param_name]
        Widgets["original"].config(state=tk.NORMAL)
        Widgets["original"].delete(0, tk.END)
        Widgets["original"].insert(0, "; ".join(self.MultiValueParams[param_name]))
        Widgets["original"].config(state="readonly")
        
        # Close dialog
        dialog.destroy()
        
        self.Logger.info(f"Added value for {param_name}: {value}")
    
    def ViewMultiValues(self, param_name):
        """View and edit all values for a multi-value parameter.
        
        Args:
            param_name: The parameter name
        """
        if param_name not in self.ParameterWidgets:
            return
        
        # Get current values
        Values = []
        if param_name in self.MultiValueParams:
            Values = self.MultiValueParams[param_name]
        else:
            CurrentValue = self.OriginalParams.get(param_name, "")
            if CurrentValue:
                Values = [CurrentValue]
        
        # Create dialog
        Dialog = tk.Toplevel(self.Parent)
        Dialog.title(f"Values for {param_name}")
        Dialog.geometry("500x300")
        Dialog.transient(self.Parent.winfo_toplevel())
        
        # Center dialog on parent window
        ParentRoot = self.Parent.winfo_toplevel()
        X = ParentRoot.winfo_x() + (ParentRoot.winfo_width() - 500) // 2
        Y = ParentRoot.winfo_y() + (ParentRoot.winfo_height() - 300) // 2
        Dialog.geometry(f"+{X}+{Y}")
        
        # Create frame for content
        Frame = ttk.Frame(Dialog, padding="10")
        Frame.pack(fill=tk.BOTH, expand=True)
        
        # Add label
        ttk.Label(Frame, text=f"Values for {param_name}:").pack(pady=(0, 5), anchor=tk.W)
        
        # Create listbox with values
        ListboxFrame = ttk.Frame(Frame)
        ListboxFrame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        Listbox = tk.Listbox(ListboxFrame, selectmode=tk.SINGLE)
        Listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        Scrollbar = ttk.Scrollbar(ListboxFrame, orient=tk.VERTICAL, command=Listbox.yview)
        Scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        Listbox.config(yscrollcommand=Scrollbar.set)
        
        # Populate listbox
        for Value in Values:
            Listbox.insert(tk.END, Value)
        
        # Add buttons for actions
        ButtonFrame = ttk.Frame(Frame)
        ButtonFrame.pack(fill=tk.X, pady=(10, 0))
        
        def AddValue():
            Dialog.deiconify()
            # Refresh listbox
            Listbox.delete(0, tk.END)
            for Value in self.MultiValueParams.get(param_name, []):
                Listbox.insert(tk.END, Value)
        
        def RemoveValue():
            Selected = Listbox.curselection()
            if not Selected:
                messagebox.showinfo("Info", "Please select a value to remove", parent=Dialog)
                return
                
            Index = Selected[0]
            if param_name in self.MultiValueParams and 0 <= Index < len(self.MultiValueParams[param_name]):
                Value = self.MultiValueParams[param_name][Index]
                Confirm = messagebox.askyesno(
                    "Confirm", 
                    f"Remove value: {Value}?", 
                    parent=Dialog
                )
                
                if Confirm:
                    self.MultiValueParams[param_name].pop(Index)
                    Listbox.delete(Index)
                    
                    # Update the original value display
                    Widgets = self.ParameterWidgets[param_name]
                    Widgets["original"].config(state=tk.NORMAL)
                    Widgets["original"].delete(0, tk.END)
                    Widgets["original"].insert(0, "; ".join(self.MultiValueParams[param_name]))
                    Widgets["original"].config(state="readonly")
        
        ttk.Button(ButtonFrame, text="Add", command=AddValue).pack(side=tk.LEFT, padx=5)
        ttk.Button(ButtonFrame, text="Remove", command=RemoveValue).pack(side=tk.LEFT, padx=5)
        ttk.Button(ButtonFrame, text="Close", command=Dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def GetChangedParameters(self):
        """Get the changed parameters.
        
        Returns:
            dict: Dictionary of changed parameters
        """
        ChangedParams = {}
        
        for ParamName, Widgets in self.ParameterWidgets.items():
            if Widgets["type"] == "entry":
                ChangedValue = Widgets["changed"].get().strip()
            else:  # combo
                ChangedValue = Widgets["changed"].get()
            
            OriginalValue = Widgets["original"].get()
            
            # Skip if unchanged
            if not ChangedValue or ChangedValue == OriginalValue:
                continue
            
            # Handle multi-value parameters
            if ParamName in self.MultiValueParams and self.ParameterHandler.IsMultiValueParameter(ParamName):
                # For multi-value params, we split by semicolon
                Values = [v.strip() for v in ChangedValue.split(";") if v.strip()]
                ChangedParams[ParamName] = Values
            else:
                # Validate the value
                if self.ParameterHandler.ValidateParameterValue(ParamName, ChangedValue):
                    ChangedParams[ParamName] = ChangedValue
                else:
                    ErrorMsg = self.ParameterHandler.GetLastValidationError()
                    messagebox.showerror("Invalid Parameter", 
                                        f"Parameter '{ParamName}' has invalid value: {ErrorMsg}")
                    Widgets["changed"].focus_set()
                    return {}
        
        # Add multi-value parameters that were modified using the UI
        for ParamName, Values in self.MultiValueParams.items():
            if ParamName not in ChangedParams:
                OriginalValue = self.OriginalParams.get(ParamName, "")
                
                if isinstance(OriginalValue, list):
                    # Compare lists
                    if sorted(OriginalValue) != sorted(Values):
                        ChangedParams[ParamName] = Values
                else:
                    # Compare single value with list
                    OriginalList = [OriginalValue] if OriginalValue else []
                    if sorted(OriginalList) != sorted(Values):
                        ChangedParams[ParamName] = Values
        
        return ChangedParams
    
    def ResetChanges(self):
        """Reset all parameter changes."""
        for ParamName, Widgets in self.ParameterWidgets.items():
            if Widgets["type"] == "entry":
                Widgets["changed"].delete(0, tk.END)
            else:  # combo
                Widgets["changed"].set("")
        
        # Reset multi-value parameters
        self.MultiValueParams = {}
        
        # Update original values
        for ParamName, Widgets in self.ParameterWidgets.items():
            OriginalValue = self.OriginalParams.get(ParamName, "")
            Widgets["original"].config(state=tk.NORMAL)
            Widgets["original"].delete(0, tk.END)
            Widgets["original"].insert(0, OriginalValue if not isinstance(OriginalValue, list) 
                                      else "; ".join(OriginalValue))
            Widgets["original"].config(state="readonly")withdraw()
            self.AddMultiValue(param_name)
            Dialog.