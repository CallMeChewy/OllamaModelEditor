# File: ParameterEditor.py
# Path: OllamaModelEditor/GUI/Components/ParameterEditor.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-13
# Description: Parameter editing component with state tracking for the OllamaModelEditor application

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox, QDoubleSpinBox,
    QPushButton, QGridLayout, QGroupBox, QTextEdit, QComboBox, QMessageBox,
    QInputDialog, QLineEdit, QFrame, QTabWidget, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QEvent, Signal, Slot
from PySide6.QtGui import QIcon, QColor, QFont
from typing import Dict, Any, Tuple, List, Optional

class ParameterEditor(QWidget):
    """Widget for editing model parameters with state tracking."""
    
    # Signal emitted when parameters are applied
    ParametersApplied = Signal(dict)
    
    def __init__(self, ModelManager, Config, StateManager):
        """
        Initialize the parameter editor.
        
        Args:
            ModelManager: Model manager instance
            Config: Configuration manager instance
            StateManager: Parameter state manager instance
        """
        super().__init__()
        
        # Store references
        self.ModelManager = ModelManager
        self.Config = Config
        self.StateManager = StateManager
        self.CurrentModel = None
        self.ParameterControls = {}
        
        # Access status bar from parent (will be set after initialization)
        self.StatusBar = None
        
        # Set up UI
        self._SetupUI()
    
    def _SetupUI(self):
        """Set up the user interface."""
        # Create layout
        Layout = QVBoxLayout()
        self.setLayout(Layout)
        
        # Add header layout with labels and presets
        HeaderLayout = QHBoxLayout()
        
        # Add header label
        HeaderLabel = QLabel("Model Parameters")
        HeaderLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        HeaderLayout.addWidget(HeaderLabel)
        
        # Add spacer
        HeaderLayout.addStretch()
        
        # Add preset selector
        PresetLayout = QHBoxLayout()
        PresetLabel = QLabel("Preset:")
        self.PresetCombo = QComboBox()
        self.LoadPresets()  # Populate presets
        
        self.SavePresetButton = QPushButton("Save Preset")
        self.SavePresetButton.setIcon(QIcon.fromTheme("document-save"))
        self.SavePresetButton.clicked.connect(self._OnSavePreset)
        
        PresetLayout.addWidget(PresetLabel)
        PresetLayout.addWidget(self.PresetCombo)
        PresetLayout.addWidget(self.SavePresetButton)
        
        HeaderLayout.addLayout(PresetLayout)
        
        Layout.addLayout(HeaderLayout)
        
        # Add tab widget for parameter editing and model file view
        self.TabWidget = QTabWidget()
        
        # Parameters tab
        self.ParametersTab = QWidget()
        ParametersLayout = QVBoxLayout(self.ParametersTab)
        
        # Create parameters section
        ParametersGroupBox = QGroupBox("Basic Parameters")
        ParamLayout = QVBoxLayout(ParametersGroupBox)
        
        # Create parameters grid
        self.ParametersGrid = QGridLayout()
        ParamLayout.addLayout(self.ParametersGrid)
        
        ParametersLayout.addWidget(ParametersGroupBox)
        
        # Add advanced parameters section
        AdvancedGroupBox = QGroupBox("Advanced Parameters")
        AdvancedGroupBox.setCheckable(True)
        AdvancedGroupBox.setChecked(False)
        AdvancedLayout = QVBoxLayout(AdvancedGroupBox)
        
        # Create advanced parameters grid
        self.AdvancedParametersGrid = QGridLayout()
        AdvancedLayout.addLayout(self.AdvancedParametersGrid)
        
        ParametersLayout.addWidget(AdvancedGroupBox)
        
        # Add parameter description section
        DescriptionGroupBox = QGroupBox("Parameter Description")
        DescriptionLayout = QVBoxLayout(DescriptionGroupBox)
        
        self.DescriptionText = QTextEdit()
        self.DescriptionText.setReadOnly(True)
        self.DescriptionText.setMinimumHeight(100)
        self.DescriptionText.setPlaceholderText("Select a parameter to see its description")
        DescriptionLayout.addWidget(self.DescriptionText)
        
        ParametersLayout.addWidget(DescriptionGroupBox)
        
        # State changes tab
        self.StateTab = QWidget()
        StateLayout = QVBoxLayout(self.StateTab)
        
        # Add state changes table
        self.StateTable = QTableWidget(0, 3)  # Rows will be added dynamically
        self.StateTable.setHorizontalHeaderLabels(["Parameter", "Original Value", "Current Value"])
        self.StateTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.StateTable.verticalHeader().setVisible(False)
        StateLayout.addWidget(self.StateTable)
        
        # Model file tab
        self.ModelFileTab = QWidget()
        ModelFileLayout = QVBoxLayout(self.ModelFileTab)
        
        self.ModelFileText = QTextEdit()
        self.ModelFileText.setReadOnly(True)
        self.ModelFileText.setLineWrapMode(QTextEdit.NoWrap)
        self.ModelFileText.setFont(QFont("Courier New", 10))
        ModelFileLayout.addWidget(self.ModelFileText)
        
        # Add tabs to the tab widget
        self.TabWidget.addTab(self.ParametersTab, "Parameters")
        self.TabWidget.addTab(self.StateTab, "State Changes")
        self.TabWidget.addTab(self.ModelFileTab, "Model File")
        
        Layout.addWidget(self.TabWidget)
        
        # Add action buttons
        ButtonFrame = QFrame()
        ButtonLayout = QHBoxLayout(ButtonFrame)
        ButtonLayout.setContentsMargins(0, 10, 0, 0)
        
        self.ApplyButton = QPushButton("Apply Changes")
        self.ApplyButton.setIcon(QIcon.fromTheme("dialog-ok-apply"))
        self.ApplyButton.clicked.connect(self._OnApplyChanges)
        ButtonLayout.addWidget(self.ApplyButton)
        
        self.ResetButton = QPushButton("Reset to Original")
        self.ResetButton.setIcon(QIcon.fromTheme("edit-undo"))
        self.ResetButton.clicked.connect(self._OnResetToOriginal)
        ButtonLayout.addWidget(self.ResetButton)
        
        self.DefaultButton = QPushButton("Reset to Default")
        self.DefaultButton.setIcon(QIcon.fromTheme("edit-clear"))
        self.DefaultButton.clicked.connect(self._OnResetToDefault)
        ButtonLayout.addWidget(self.DefaultButton)
        
        Layout.addWidget(ButtonFrame)
        
        # Add placeholder message (hidden initially)
        self.PlaceholderLabel = QLabel("Select a model to edit parameters")
        self.PlaceholderLabel.setAlignment(Qt.AlignCenter)
        self.PlaceholderLabel.setVisible(False)
        Layout.addWidget(self.PlaceholderLabel)
    
    def SetStatusBar(self, StatusBar):
        """
        Set the status bar reference.
        
        Args:
            StatusBar: Status bar widget
        """
        self.StatusBar = StatusBar
    
    def LoadModel(self, ModelName: str):
        """
        Load a model for editing.
        
        Args:
            ModelName: Name of the model to load
        """
        # Store current model
        self.CurrentModel = ModelName
        
        # Hide placeholder
        self.PlaceholderLabel.setVisible(False)
        
        # Load model state
        OriginalState, CurrentState = self.StateManager.LoadModelState(ModelName)
        
        # Clear parameters grid
        self._ClearParameterGrids()
        
        # Clear parameter controls
        self.ParameterControls = {}
        
        # Get parameter descriptions from database if available
        ParameterDescriptions = {}
        if self.Config.DB:
            # Get all parameters
            Parameters = self.Config.DB.GetAllParameters()
            for Param in Parameters:
                ParameterDescriptions[Param['Name']] = Param['Description']
        
        # Add parameter controls
        self._CreateParameterControl(
            "Temperature", 
            CurrentState.get('Temperature', 0.7), 
            0.0, 2.0, 0.1, 
            False,
            ParameterDescriptions.get('Temperature', '')
        )
        
        self._CreateParameterControl(
            "TopP", 
            CurrentState.get('TopP', 0.9), 
            0.0, 1.0, 0.01, 
            False,
            ParameterDescriptions.get('TopP', '')
        )
        
        self._CreateParameterControl(
            "MaxTokens", 
            CurrentState.get('MaxTokens', 2048), 
            1, 32000, 1, 
            True,
            ParameterDescriptions.get('MaxTokens', '')
        )
        
        self._CreateParameterControl(
            "FrequencyPenalty", 
            CurrentState.get('FrequencyPenalty', 0.0), 
            0.0, 2.0, 0.1, 
            False,
            ParameterDescriptions.get('FrequencyPenalty', '')
        )
        
        self._CreateParameterControl(
            "PresencePenalty", 
            CurrentState.get('PresencePenalty', 0.0), 
            0.0, 2.0, 0.1, 
            False,
            ParameterDescriptions.get('PresencePenalty', '')
        )
        
        # Update state table
        self._UpdateStateTable()
        
        # Update model file view
        self._UpdateModelFileView()
        
        # Set preset to "Custom" (will be updated if it matches a preset)
        Index = self.PresetCombo.findText("Custom")
        if Index >= 0:
            self.PresetCombo.setCurrentIndex(Index)
        
        # Check if current state matches a preset
        self._CheckForMatchingPreset(CurrentState)
    
    def _ClearParameterGrids(self):
        """Clear parameter grid layouts."""
        # Clear basic parameters grid
        while self.ParametersGrid.count():
            Item = self.ParametersGrid.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
        
        # Clear advanced parameters grid
        while self.AdvancedParametersGrid.count():
            Item = self.AdvancedParametersGrid.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
    
    def _CreateParameterControl(self, Name, Value, Min, Max, Step, IsInteger=False, Description=""):
        """
        Add a parameter control to the grid.
        
        Args:
            Name: Parameter name
            Value: Current value
            Min: Minimum value
            Max: Maximum value
            Step: Step size
            IsInteger: Whether the parameter is an integer
            Description: Parameter description
        """
        # Determine which grid to use
        if Name in ["Temperature", "TopP", "MaxTokens"]:
            Grid = self.ParametersGrid
            Row = Grid.rowCount()
        else:
            Grid = self.AdvancedParametersGrid
            Row = Grid.rowCount()
        
        # Add label
        Label = QLabel(f"{Name}:")
        Grid.addWidget(Label, Row, 0)
        
        # Add slider
        Slider = QSlider(Qt.Horizontal)
        if IsInteger:
            Slider.setMinimum(int(Min))
            Slider.setMaximum(int(Max))
            Slider.setValue(int(Value))
        else:
            Slider.setMinimum(int(Min * 100))
            Slider.setMaximum(int(Max * 100))
            Slider.setValue(int(Value * 100))
        Grid.addWidget(Slider, Row, 1)
        
        # Add spin box
        if IsInteger:
            SpinBox = QSpinBox()
            SpinBox.setMinimum(int(Min))
            SpinBox.setMaximum(int(Max))
            SpinBox.setValue(int(Value))
        else:
            SpinBox = QDoubleSpinBox()
            SpinBox.setMinimum(Min)
            SpinBox.setMaximum(Max)
            SpinBox.setSingleStep(Step)
            SpinBox.setValue(Value)
            SpinBox.setDecimals(2)
        Grid.addWidget(SpinBox, Row, 2)
        
        # Store parameter description
        Slider.setProperty("ParameterName", Name)
        Slider.setProperty("ParameterDescription", Description)
        SpinBox.setProperty("ParameterName", Name)
        SpinBox.setProperty("ParameterDescription", Description)
        
        # Connect signals
        if IsInteger:
            Slider.valueChanged.connect(SpinBox.setValue)
            SpinBox.valueChanged.connect(Slider.setValue)
        else:
            Slider.valueChanged.connect(lambda v: SpinBox.setValue(v / 100))
            SpinBox.valueChanged.connect(lambda v: Slider.setValue(int(v * 100)))
        
        # Connect update signals
        Slider.valueChanged.connect(lambda: self._OnParameterChanged(Name))
        SpinBox.valueChanged.connect(lambda: self._OnParameterChanged(Name))
        
        # Connect description update signals
        Slider.sliderPressed.connect(lambda: self._UpdateDescription(Name, Description))
        SpinBox.installEventFilter(self)
        
        # Store controls for later access
        self.ParameterControls[Name] = (Slider, SpinBox)
    
    def eventFilter(self, obj, event):
        """Handle focus events for parameter controls."""
        if event.type() == QEvent.FocusIn:
            # If it's a parameter control, update description
            ParameterName = obj.property("ParameterName")
            if ParameterName:
                Description = obj.property("ParameterDescription")
                self._UpdateDescription(ParameterName, Description)
        
        return super().eventFilter(obj, event)
    
    def _UpdateDescription(self, ParameterName, Description):
        """
        Update the parameter description text.
        
        Args:
            ParameterName: Name of the parameter
            Description: Description text
        """
        # Get parameter descriptions from database if available
        if self.Config.DB:
            # Try to get from database
            Parameter = self.Config.DB.GetParameter(ParameterName)
            if Parameter and Parameter.get('Description'):
                Description = Parameter.get('Description')
        
        # If no description is available, use predefined descriptions
        if not Description:
            Descriptions = {
                "Temperature": "Controls randomness in text generation. Higher values (0.7-1.0) produce more creative outputs, while lower values (0.2-0.5) make output more focused and deterministic.",
                "TopP": "Controls diversity via nucleus sampling. Lower values make output more focused on likely tokens. 0.9 is a good starting point.",
                "MaxTokens": "The maximum length of the generated text. Higher values allow for longer responses but consume more resources.",
                "FrequencyPenalty": "Reduces repetition by penalizing tokens that have already appeared in the text. Higher values (0.5-1.0) strongly discourage repetition.",
                "PresencePenalty": "Penalizes tokens that have appeared at all, encouraging the model to discuss new topics. Useful for keeping responses diverse."
            }
            Description = Descriptions.get(ParameterName, f"No description available for {ParameterName}")
        
        # Update the description text
        self.DescriptionText.setHtml(f"<h3>{ParameterName}</h3>\n<p>{Description}</p>")
    
    def _OnParameterChanged(self, ParameterName):
        """
        Handle parameter value change.
        
        Args:
            ParameterName: Name of the changed parameter
        """
        if not self.CurrentModel:
            return
        
        # Get current parameter values
        Params = self._GetParametersFromControls()
        
        # Update state manager
        self.StateManager.UpdateCurrentState(self.CurrentModel, Params)
        
        # Update state table
        self._UpdateStateTable()
        
        # Check if current state matches a preset
        self._CheckForMatchingPreset(Params)
    
    def _UpdateStateTable(self):
        """Update the state changes table."""
        if not self.CurrentModel:
            return
        
        # Get state differences
        Differences = self.StateManager.GetStateDifferences(self.CurrentModel)
        
        # Clear table
        self.StateTable.setRowCount(0)
        
        # Add differences to table
        Row = 0
        for Param, (OrigValue, CurrValue) in Differences.items():
            self.StateTable.insertRow(Row)
            
            # Add parameter name
            ParamItem = QTableWidgetItem(Param)
            ParamItem.setFlags(ParamItem.flags() & ~Qt.ItemIsEditable)
            self.StateTable.setItem(Row, 0, ParamItem)
            
            # Add original value
            OrigItem = QTableWidgetItem(str(OrigValue))
            OrigItem.setFlags(OrigItem.flags() & ~Qt.ItemIsEditable)
            self.StateTable.setItem(Row, 1, OrigItem)
            
            # Add current value (highlighted)
            CurrItem = QTableWidgetItem(str(CurrValue))
            CurrItem.setFlags(CurrItem.flags() & ~Qt.ItemIsEditable)
            CurrItem.setBackground(QColor(255, 255, 0, 100))  # Light yellow highlight
            self.StateTable.setItem(Row, 2, CurrItem)
            
            Row += 1
    
    def _UpdateModelFileView(self):
        """Update the model file view."""
        if not self.CurrentModel:
            return
        
        # Get model file content
        ModelFile = self.StateManager.GetModelFile(self.CurrentModel)
        
        if ModelFile:
            # Format as pretty JSON
            ModelFileText = json.dumps(ModelFile, indent=2)
            self.ModelFileText.setText(ModelFileText)
        else:
            self.ModelFileText.setText("Model file not available")
    
    def LoadPresets(self):
        """Load available presets into the preset combo box."""
        self.PresetCombo.clear()
        
        # Add "Custom" option (for current state)
        self.PresetCombo.addItem("Custom")
        
        # Add built-in presets
        BuiltInPresets = ["Default", "Creative", "Precise", "Fast", "Balanced"]
        for Preset in BuiltInPresets:
            self.PresetCombo.addItem(Preset)
        
        # Add user presets from database if available
        if self.Config.DB:
            UserPresets = self.Config.DB.GetUserPresets()
            for Preset in UserPresets:
                self.PresetCombo.addItem(Preset.get('Name', 'Unknown'))
        
        # Connect signal
        self.PresetCombo.currentTextChanged.connect(self._OnPresetSelected)
    
    def _CheckForMatchingPreset(self, Params):
        """
        Check if current parameters match a preset.
        
        Args:
            Params: Current parameters
        """
        # Get all presets
        Presets = self.ModelManager.GetAllPresets()
        
        # Compare with each preset
        for Preset in Presets:
            PresetName = Preset.get('Name')
            if PresetName == "Custom":
                continue
            
            PresetParams = self.ModelManager.GetPresetParameters(PresetName)
            
            # Check if parameters match
            Matches = True
            for Key, Value in PresetParams.items():
                if Key in Params and abs(Params[Key] - Value) > 0.001:
                    Matches = False
                    break
            
            if Matches:
                # Set preset combo to matching preset
                Index = self.PresetCombo.findText(PresetName)
                if Index >= 0:
                    self.PresetCombo.blockSignals(True)
                    self.PresetCombo.setCurrentIndex(Index)
                    self.PresetCombo.blockSignals(False)
                return
        
        # If no match found, set to "Custom"
        Index = self.PresetCombo.findText("Custom")
        if Index >= 0:
            self.PresetCombo.blockSignals(True)
            self.PresetCombo.setCurrentIndex(Index)
            self.PresetCombo.blockSignals(False)
    
    def _OnPresetSelected(self, PresetName):
        """
        Handle preset selection.
        
        Args:
            PresetName: Name of the selected preset
        """
        if not self.CurrentModel or PresetName == "Custom":
            return
        
        # Get preset parameters
        PresetParams = self.ModelManager.GetPresetParameters(PresetName)
        
        if not PresetParams:
            return
        
        # Apply preset parameters to controls
        self._ApplyParametersToControls(PresetParams)
        
        # Update state manager
        self.StateManager.UpdateCurrentState(self.CurrentModel, PresetParams)
        
        # Update state table
        self._UpdateStateTable()
    
    def _OnSavePreset(self):
        """Handle save preset button click."""
        # Get current parameter values
        Params = self._GetParametersFromControls()
        
        # Prompt user for preset name
        PresetName, OK = QInputDialog.getText(
            self,
            "Save Preset",
            "Enter a name for this preset:",
            QLineEdit.Normal,
            ""
        )
        
        if not OK or not PresetName:
            return
        
        # Prompt for description
        Description, OK = QInputDialog.getText(
            self,
            "Preset Description",
            "Enter a description for this preset:",
            QLineEdit.Normal,
            ""
        )
        
        if not OK:
            Description = ""
        
        # Save preset
        Success = self.ModelManager.SaveUserPreset(PresetName, Description, Params)
        
        if Success:
            # Update preset list
            self.LoadPresets()
            
            # Select the new preset
            Index = self.PresetCombo.findText(PresetName)
            if Index >= 0:
                self.PresetCombo.setCurrentIndex(Index)
        else:
            # Show error message
            QMessageBox.warning(
                self,
                "Save Error",
                "Error saving preset. Please check the logs for details."
            )
    
    def _GetParametersFromControls(self):
        """
        Get parameter values from controls.
        
        Returns:
            Dict: Parameter values
        """
        Params = {}
        
        for Name, (Slider, SpinBox) in self.ParameterControls.items():
            Params[Name] = SpinBox.value()
        
        return Params
    
    def _ApplyParametersToControls(self, Params):
        """
        Apply parameter values to controls.
        
        Args:
            Params: Dictionary of parameter values
        """
        for Name, Value in Params.items():
            if Name in self.ParameterControls:
                Slider, SpinBox = self.ParameterControls[Name]
                
                # Block signals to prevent recursive updates
                SpinBox.blockSignals(True)
                Slider.blockSignals(True)
                
                SpinBox.setValue(Value)
                
                # Set slider value (scaled for non-integer values)
                if isinstance(SpinBox, QDoubleSpinBox):
                    Slider.setValue(int(Value * 100))
                else:
                    Slider.setValue(Value)
                
                # Unblock signals
                SpinBox.blockSignals(False)
                Slider.blockSignals(False)
        
        # Trigger parameter changed event for each parameter
        for Name in Params.keys():
            if Name in self.ParameterControls:
                self._OnParameterChanged(Name)
    
    def _OnApplyChanges(self):
        """Handle apply changes button click."""
        if not self.CurrentModel:
            return
        
        # Get parameter values
        Params = self._GetParametersFromControls()
        
        # Update model parameters
        Success = self.ModelManager.UpdateModelParameters(self.CurrentModel, Params)
        
        if Success:
            # Commit current state
            self.StateManager.CommitCurrentState(self.CurrentModel)
            
            # Update state table
            self._UpdateStateTable()
            
            # Show success message
            if self.StatusBar:
                self.StatusBar.showMessage(f"Parameters updated for {self.CurrentModel}", 3000)
            
            # Set preset to "Custom"
            Index = self.PresetCombo.findText("Custom")
            if Index >= 0:
                self.PresetCombo.setCurrentIndex(Index)
            
            # Check if now matches a preset
            self._CheckForMatchingPreset(Params)
            
            # Emit signal
            self.ParametersApplied.emit(Params)
        else:
            # Show error message
            QMessageBox.warning(
                self,
                "Update Error",
                f"Failed to update parameters for {self.CurrentModel}"
            )
    
    def _OnResetToOriginal(self):
        """Handle reset to original button click."""
        if not self.CurrentModel:
            return
        
        # Reset to original state
        OriginalParams = self.StateManager.ResetToOriginal(self.CurrentModel)
        
        if OriginalParams:
            # Apply original parameters to controls
            self._ApplyParametersToControls(OriginalParams)
            
            # Update state table
            self._UpdateStateTable()
            
            # Show message
            if self.StatusBar:
                self.StatusBar.showMessage("Parameters reset to original values", 3000)
    
    def _OnResetToDefault(self):
        """Handle reset to default button click."""
        if not self.CurrentModel:
            return
        
        # Get default parameters
        DefaultParams = self.Config.GetModelConfig('DefaultParameters')
        
        # Apply default parameters to controls
        self._ApplyParametersToControls(DefaultParams)
        
        # Update state manager
        self.StateManager.UpdateCurrentState(self.CurrentModel, DefaultParams)
        
        # Update state table
        self._UpdateStateTable()
        
        # Show message
        if self.StatusBar:
            self.StatusBar.showMessage("Parameters reset to default values", 3000)