# File: ParameterEditor.py
# Path: OllamaModelEditor/GUI/Components/ParameterEditor.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-12 15:00PM
# Description: Parameter editing component for the OllamaModelEditor application

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QSlider, QSpinBox, 
    QDoubleSpinBox, QHBoxLayout, QComboBox, QPushButton, QFrame,
    QFormLayout, QMessageBox, QDialog, QDialogButtonBox, QLineEdit,
    QTextEdit, QGroupBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

from typing import Dict, Any, Optional, List

class ParameterEditor(QWidget):
    """Widget for editing model parameters."""
    
    # Signal emitted when parameters are updated
    ParametersUpdated = Signal(dict)
    
    def __init__(self, ModelManager, Config):
        """
        Initialize the parameter editor.
        
        Args:
            ModelManager: Model manager instance
            Config: Configuration manager instance
        """
        super().__init__()
        
        # Store references
        self.ModelManager = ModelManager
        self.Config = Config
        self.DB = getattr(Config, 'DB', None)
        self.CurrentModel = None
        self.Parameters = {}
        self.ParameterControls = {}
        
        # Set up UI
        self._SetupUI()
    
    def _SetupUI(self):
        """Set up the user interface."""
        # Create layout
        Layout = QVBoxLayout()
        self.setLayout(Layout)
        
        # Add header layout
        HeaderLayout = QHBoxLayout()
        
        # Add header label
        HeaderLabel = QLabel("Model Parameters")
        HeaderLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        HeaderLayout.addWidget(HeaderLabel)
        
        # Add stretch to push preset controls to right
        HeaderLayout.addStretch()
        
        # Add preset selector
        PresetLabel = QLabel("Preset:")
        HeaderLayout.addWidget(PresetLabel)
        
        self.PresetCombo = QComboBox()
        self.PresetCombo.currentTextChanged.connect(self._OnPresetSelected)
        HeaderLayout.addWidget(self.PresetCombo)
        
        self.SavePresetButton = QPushButton("Save Preset")
        self.SavePresetButton.clicked.connect(self._OnSavePreset)
        HeaderLayout.addWidget(self.SavePresetButton)
        
        Layout.addLayout(HeaderLayout)
        
        # Add separator line
        Separator = QFrame()
        Separator.setFrameShape(QFrame.HLine)
        Separator.setFrameShadow(QFrame.Sunken)
        Layout.addWidget(Separator)
        
        # Create parameters frame with scrolling
        self.ParametersFrame = QFrame()
        
        # Create parameters layout
        self.ParametersLayout = QFormLayout(self.ParametersFrame)
        self.ParametersLayout.setVerticalSpacing(12)
        self.ParametersLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Add placeholder message
        self.PlaceholderLabel = QLabel("Select a model to edit parameters")
        self.PlaceholderLabel.setAlignment(Qt.AlignCenter)
        self.ParametersLayout.addRow(self.PlaceholderLabel)
        
        Layout.addWidget(self.ParametersFrame)
        
        # Create parameter description section
        DescriptionFrame = QFrame()
        DescriptionLayout = QVBoxLayout(DescriptionFrame)
        
        DescriptionLabel = QLabel("Parameter Description")
        DescriptionLabel.setStyleSheet("font-weight: bold;")
        DescriptionLayout.addWidget(DescriptionLabel)
        
        self.DescriptionText = QTextEdit()
        self.DescriptionText.setReadOnly(True)
        self.DescriptionText.setMaximumHeight(100)
        self.DescriptionText.setPlaceholderText("Select a parameter to see its description")
        DescriptionLayout.addWidget(self.DescriptionText)
        
        Layout.addWidget(DescriptionFrame)
        
        # Add buttons layout
        ButtonsLayout = QHBoxLayout()
        
        self.ApplyButton = QPushButton("Apply Changes")
        self.ApplyButton.clicked.connect(self._OnApplyChanges)
        self.ApplyButton.setEnabled(False)
        ButtonsLayout.addWidget(self.ApplyButton)
        
        self.ResetButton = QPushButton("Reset to Default")
        self.ResetButton.clicked.connect(self._OnResetToDefault)
        self.ResetButton.setEnabled(False)
        ButtonsLayout.addWidget(self.ResetButton)
        
        Layout.addLayout(ButtonsLayout)
        
        # Load presets
        self._LoadPresets()
    
    def _LoadPresets(self):
        """Load parameter presets."""
        # Clear combo box
        self.PresetCombo.clear()
        
        # Add standard presets
        self.PresetCombo.addItem("Custom")
        
        # Add standard presets from database or fallback to hardcoded
        if self.DB:
            # Load presets from database
            try:
                Presets = self.DB.GetPresets()
                for Preset in Presets:
                    self.PresetCombo.addItem(Preset["Name"])
            except Exception as Error:
                print(f"Error loading presets from database: {Error}")
                # Fall back to hardcoded presets
                self._AddHardcodedPresets()
        else:
            # Use hardcoded presets
            self._AddHardcodedPresets()
        
        # Add user presets
        try:
            if self.DB:
                UserPresets = self.ModelManager.GetUserPresets()
                if UserPresets:
                    # Add separator
                    self.PresetCombo.insertSeparator(self.PresetCombo.count())
                    
                    # Add user presets
                    for Preset in UserPresets:
                        self.PresetCombo.addItem(Preset["Name"] + " (User)")
        except Exception as Error:
            print(f"Error loading user presets: {Error}")
    
    def _AddHardcodedPresets(self):
        """Add hardcoded presets to combo box."""
        StandardPresets = ["Default", "Creative", "Precise", "Fast", "Balanced", "Deterministic"]
        for Preset in StandardPresets:
            self.PresetCombo.addItem(Preset)
    
    def LoadModel(self, ModelName):
        """
        Load a model for editing.
        
        Args:
            ModelName: Name of the model to load
        """
        # Store current model
        self.CurrentModel = ModelName
        
        # Hide placeholder
        self.PlaceholderLabel.setVisible(False)
        
        # Clear parameters layout
        self._ClearParametersLayout()
        
        # Get model parameters
        self.Parameters = self.Config.GetModelConfig(ModelName)
        
        # Enable buttons
        self.ApplyButton.setEnabled(True)
        self.ResetButton.setEnabled(True)
        
        # Get parameter definitions from database or fallback to hardcoded
        if self.DB:
            try:
                # Get parameter definitions from database
                ParameterDefs = self.DB.GetAllParameters()
                
                # Add parameter controls based on definitions
                if ParameterDefs:
                    for Param in ParameterDefs:
                        self._AddParameterControl(
                            Param["Name"],
                            Param["DisplayName"],
                            self.Parameters.get(Param["Name"], Param["DefaultValue"]),
                            Param["MinValue"],
                            Param["MaxValue"],
                            Param["StepSize"],
                            Param["IsInteger"],
                            Param["Description"]
                        )
                else:
                    # Fallback to hardcoded parameters
                    self._AddHardcodedParameters()
            except Exception as Error:
                print(f"Error loading parameter definitions: {Error}")
                # Fallback to hardcoded parameters
                self._AddHardcodedParameters()
        else:
            # Use hardcoded parameters
            self._AddHardcodedParameters()
    
    def _ClearParametersLayout(self):
        """Clear all parameter controls from layout."""
        # Clear parameter controls dictionary
        self.ParameterControls = {}
        
        # Remove all items from layout
        while self.ParametersLayout.count():
            Item = self.ParametersLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
    
    def _AddHardcodedParameters(self):
        """Add hardcoded parameter controls."""
        # Add basic parameters
        self._AddParameterControl(
            "Temperature",
            "Temperature",
            self.Parameters.get("Temperature", 0.7),
            0.0, 2.0, 0.1, False,
            "Controls randomness in text generation. Higher values (0.7-1.0) produce more creative outputs, "
            "while lower values (0.2-0.5) make output more focused and deterministic."
        )
        
        self._AddParameterControl(
            "TopP",
            "Top-P",
            self.Parameters.get("TopP", 0.9),
            0.0, 1.0, 0.01, False,
            "Controls diversity via nucleus sampling. Lower values make output more focused on likely tokens. "
            "0.9 is a good starting point."
        )
        
        self._AddParameterControl(
            "MaxTokens",
            "Max Tokens",
            self.Parameters.get("MaxTokens", 2048),
            1, 32000, 1, True,
            "The maximum length of the generated text. Higher values allow for longer responses "
            "but consume more resources."
        )
        
        # Add advanced parameters
        AdvancedGroup = QGroupBox("Advanced Parameters")
        AdvancedLayout = QFormLayout(AdvancedGroup)
        
        # Frequency penalty control
        FreqPenaltyLayout = QHBoxLayout()
        FreqPenaltySlider = QSlider(Qt.Horizontal)
        FreqPenaltySlider.setMinimum(0)
        FreqPenaltySlider.setMaximum(200)
        FreqPenaltySlider.setValue(int(self.Parameters.get("FrequencyPenalty", 