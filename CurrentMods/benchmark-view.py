# File: BenchmarkView.py
# Path: OllamaModelEditor/GUI/Components/BenchmarkView.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-13
# Description: Benchmarking component with state tracking for the OllamaModelEditor application

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, 
    QFormLayout, QSpinBox, QCheckBox, QTabWidget, QApplication, QFileDialog,
    QFrame, QGridLayout, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QDialogButtonBox, QGroupBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QIcon, QFont, QColor
import json
import time
import datetime
from typing import Dict, Any, List, Optional, Tuple

class ModelStateDialog(QDialog):
    """Dialog to show model state during benchmarking."""
    
    def __init__(self, ModelName, StateManager, Parent=None):
        """
        Initialize the model state dialog.
        
        Args:
            ModelName: Name of the model
            StateManager: Parameter state manager instance
            Parent: Parent widget
        """
        super().__init__(Parent)
        
        self.ModelName = ModelName
        self.StateManager = StateManager
        
        self.setWindowTitle(f"Model State - {ModelName}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self._SetupUI()
    
    def _SetupUI(self):
        """Set up the dialog UI."""
        Layout = QVBoxLayout(self)
        
        # Add state information
        StateLabel = QLabel(f"Current state for model: <b>{self.ModelName}</b>")
        Layout.addWidget(StateLabel)
        
        # Add state table
        self.StateTable = QTableWidget(0, 3)
        self.StateTable.setHorizontalHeaderLabels(["Parameter", "Original Value", "Current Value"])
        self.StateTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.StateTable.verticalHeader().setVisible(False)
        Layout.addWidget(self.StateTable)
        
        # Update state table
        self._UpdateStateTable()
        
        # Add button box
        ButtonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        ButtonBox.accepted.connect(self.accept)
        Layout.addWidget(ButtonBox)
    
    def _UpdateStateTable(self):
        """Update the state changes table."""
        # Get state differences
        Differences = self.StateManager.GetStateDifferences(self.ModelName)
        
        # Get all parameters
        AllParams = self.StateManager.GetAllModelParameters(self.ModelName)
        
        # Clear table
        self.StateTable.setRowCount(0)
        
        # Add all parameters to table
        Row = 0
        for Param, Value in AllParams.items():
            self.StateTable.insertRow(Row)
            
            # Add parameter name
            ParamItem = QTableWidgetItem(Param)
            ParamItem.setFlags(ParamItem.flags() & ~Qt.ItemIsEditable)
            self.StateTable.setItem(Row, 0, ParamItem)
            
            # Get original and current values
            OrigValue = self.StateManager.OriginalStates.get(self.ModelName, {}).get(Param, Value)
            CurrValue = self.StateManager.CurrentStates.get(self.ModelName, {}).get(Param, Value)
            
            # Add original value
            OrigItem = QTableWidgetItem(str(OrigValue))
            OrigItem.setFlags(OrigItem.flags() & ~Qt.ItemIsEditable)
            self.StateTable.setItem(Row, 1, OrigItem)
            
            # Add current value
            CurrItem = QTableWidgetItem(str(CurrValue))
            CurrItem.setFlags(CurrItem.flags() & ~Qt.ItemIsEditable)
            
            # Highlight if different from original
            if Param in Differences:
                CurrItem.setBackground(QColor(255, 255, 0, 100))  # Light yellow highlight
            
            self.StateTable.set