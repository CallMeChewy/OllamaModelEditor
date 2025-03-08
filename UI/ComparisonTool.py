# File: ComparisonTool.py
# Path: OllamaModelEditor/UI/ComparisonTool.py
# Standard: AIDEV-PascalCase-1.0

import tkinter as tk
from tkinter import ttk, messagebox
import csv
from tkinter import filedialog

class ComparisonTool:
    """Tool for comparing parameters between models."""
    
    def __init__(self, parent, model_manager, theme_manager):
        """Initialize the comparison tool.
        
        Args:
            parent: Parent window
            model_manager: The model manager instance
            theme_manager: The theme manager instance
        """
        self.Parent = parent
        self.ModelManager = model_manager
        self.ThemeManager = theme_manager
        self.Dialog = None
        self.Tree = None
        self.Model1Combo = None
        self.Model2Combo = None
    
    def Show(self):
        """Display the comparison dialog."""
        # Check if we have enough models to compare
        Models = self.ModelManager.GetModelList()
        if not Models or len(Models) < 2:
            messagebox.showinfo("Info", "You need at least two models to compare")
            return
        
        # Create comparison dialog
        self.Dialog = tk.Toplevel(self.Parent)
        self.Dialog.title("Compare Models")
        self.Dialog.geometry("800x600")
        self.Dialog.transient(self.Parent)
        
        # Apply current theme
        self.ThemeManager.ApplyTheme(self.Dialog)
        
        # Center dialog on parent window
        X = self.Parent.winfo_x() + (self.Parent.winfo_width() - 800) // 2
        Y = self.Parent.winfo_y() + (self.Parent.winfo_height() - 600) // 2
        self.Dialog.geometry(f"+{X}+{Y}")
        
        # Create frame for content
        Frame = ttk.Frame(self.Dialog, padding="10")
        Frame.pack(fill=tk.BOTH, expand=True)
        
        # Create model selection section
        SelectFrame = ttk.Frame(Frame)
        SelectFrame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(SelectFrame, text="Model 1:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.Model1Combo = ttk.Combobox(SelectFrame, values=Models, width=30, state="readonly")
        self.Model1Combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(SelectFrame, text="Model 2:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.Model2Combo = ttk.Combobox(SelectFrame, values=Models, width=30, state="readonly")
        self.Model2Combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Set initial selections
        if Models:
            self.Model1Combo.set(Models[0])
            if len(Models) > 1:
                self.Model2Combo.set(Models[1])
        
        # Create button to perform comparison
        CompareBtn = ttk.Button(
            SelectFrame, 
            text="Compare", 
            command=self.PerformComparison
        )
        CompareBtn.grid(row=0, column=4, padx=5, pady=5)
        
        # Create treeview for results
        ResultFrame = ttk.Frame(Frame)
        ResultFrame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview with scrollbar
        TreeFrame = ttk.Frame(ResultFrame)
        TreeFrame.pack(fill=tk.BOTH, expand=True)
        
        Columns = ("model1_value", "model2_value", "difference")
        self.Tree = ttk.Treeview(TreeFrame, columns=Columns)
        
        # Set column headings
        self.Tree.heading("#0", text="Parameter")
        self.Tree.heading("model1_value", text="Model 1 Value")
        self.Tree.heading("model2_value", text="Model 2 Value")
        self.Tree.heading("difference", text="Difference")
        
        # Configure columns
        self.Tree.column("#0", width=150)
        self.Tree.column("model1_value", width=200)
        self.Tree.column("model2_value", width=200)
        self.Tree.column("difference", width=200)
        
        # Add vertical scrollbar
        VerticalScrollbar = ttk.Scrollbar(TreeFrame, orient=tk.VERTICAL, command=self.Tree.yview)
        self.Tree.configure(yscrollcommand=VerticalScrollbar.set)
        
        # Layout
        self.Tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        VerticalScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame at bottom
        ButtonFrame = ttk.Frame(Frame)
        ButtonFrame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            ButtonFrame, 
            text="Export Comparison", 
            command=self.ExportComparison
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            ButtonFrame, 
            text="Close", 
            command=self.Dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Initial comparison if both models are selected
        if self.Model1Combo.get() and self.Model2Combo.get():
            self.PerformComparison()
    
    def PerformComparison(self):
        """Perform comparison between two models."""
        Model1Name = self.Model1Combo.get()
        Model2Name = self.Model2Combo.get()
        
        if not Model1Name or not Model2Name:
            messagebox.showinfo("Info", "Please select two models to compare", parent=self.Dialog)
            return
        
        if Model1Name == Model2Name:
            messagebox.showinfo("Info", "Please select different models to compare", parent=self.Dialog)
            return
        
        # Clear previous results
        for Item in self.Tree.get_children():
            self.Tree.delete(Item)
        
        try:
            # Get parameters for first model
            Params1 = self.ModelManager.GetModelParameters(Model1Name)
            
            # Get parameters for second model
            Params2 = self.ModelManager.GetModelParameters(Model2Name)
            
            # Compare parameters
            AllParams = sorted(list(set(list(Params1.keys()) + list(Params2.keys()))))
            
            for Param in AllParams:
                Value1 = Params1.get(Param, "N/A")
                Value2 = Params2.get(Param, "N/A")
                
                # Format multi-value parameters
                if isinstance(Value1, list):
                    Value1 = "; ".join(Value1)
                if isinstance(Value2, list):
                    Value2 = "; ".join(Value2)
                
                # Calculate difference/similarity
                if Value1 == "N/A" or Value2 == "N/A":
                    Difference = "One model missing parameter"
                elif Value1 == Value2:
                    Difference = "Identical"
                else:
                    # Try to calculate numeric difference
                    try:
                        V1 = float(Value1)
                        V2 = float(Value2)
                        Diff = V2 - V1
                        Difference = f"{Diff:+.2f}" + (f" ({(Diff/V1)*100:+.2f}%)" if V1 != 0 else "")
                    except (ValueError, TypeError):
                        Difference = "Different values"
                
                # Add to tree
                self.Tree.insert("", "end", text=Param, values=(Value1, Value2, Difference))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error comparing models: {e}", parent=self.Dialog)
    
    def ExportComparison(self):
        """Export the comparison results to a file."""
        if not self.Tree.get_children():
            messagebox.showinfo("Info", "No comparison results to export", parent=self.Dialog)
            return
        
        Model1Name = self.Model1Combo.get()
        Model2Name = self.Model2Combo.get()
        
        # Ask for file location
        Filename = filedialog.asksaveasfilename(
            parent=self.Dialog,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"{Model1Name}_vs_{Model2Name}.csv"
        )
        
        if not Filename:
            return
        
        try:
            with open(Filename, "w", newline="") as f:
                Writer = csv.writer(f)
                Writer.writerow(["Parameter", f"{Model1Name} Value", f"{Model2Name} Value", "Difference"])
                
                for Item in self.Tree.get_children():
                    Param = self.Tree.item(Item, "text")
                    Values = self.Tree.item(Item, "values")
                    Writer.writerow([Param, Values[0], Values[1], Values[2]])
            
            messagebox.showinfo("Success", f"Comparison exported to {Filename}", parent=self.Dialog)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting comparison: {e}", parent=self.Dialog)
