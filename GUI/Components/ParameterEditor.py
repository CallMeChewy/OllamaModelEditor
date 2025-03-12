# File: ParameterEditor.py
# Path: OllamaModelEditor/GUI/Components/ParameterEditor.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Parameter editing component for the OllamaModelEditor application

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QSlider, QSpinBox, QDoubleSpinBox
from PySide6.QtCore import Qt

class ParameterEditor(QWidget):
    """Widget for editing model parameters."""
    
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
        self.CurrentModel = None
        
        # Set up UI
        self._SetupUI()
    
    def _SetupUI(self):
        """Set up the user interface."""
        # Create layout
        Layout = QVBoxLayout()
        self.setLayout(Layout)
        
        # Add header label
        HeaderLabel = QLabel("Model Parameters:")
        Layout.addWidget(HeaderLabel)
        
        # Create parameters grid
        self.ParametersGrid = QGridLayout()
        Layout.addLayout(self.ParametersGrid)
        
        # Add placeholder message
        self.PlaceholderLabel = QLabel("Select a model to edit parameters")
        self.PlaceholderLabel.setAlignment(Qt.AlignCenter)
        Layout.addWidget(self.PlaceholderLabel)
        
        # Add stretch to bottom
        Layout.addStretch()
    
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
        
        # Clear parameters grid
        while self.ParametersGrid.count():
            Item = self.ParametersGrid.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
        
        # Get model parameters
        ModelParams = self.Config.GetModelConfig(ModelName)
        
        # Add parameter controls
        self._AddParameterControl("Temperature", ModelParams.get('Temperature', 0.7), 0.0, 2.0, 0.1)
        self._AddParameterControl("TopP", ModelParams.get('TopP', 0.9), 0.0, 1.0, 0.01)
        self._AddParameterControl("MaxTokens", ModelParams.get('MaxTokens', 2048), 1, 32000, 1, True)
    
    def _AddParameterControl(self, Name, Value, Min, Max, Step, IsInteger=False):
        """
        Add a parameter control to the grid.
        
        Args:
            Name: Parameter name
            Value: Current value
            Min: Minimum value
            Max: Maximum value
            Step: Step size
            IsInteger: Whether the parameter is an integer
        """
        # Determine next row
        Row = self.ParametersGrid.rowCount()
        
        # Add label
        Label = QLabel(f"{Name}:")
        self.ParametersGrid.addWidget(Label, Row, 0)
        
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
        self.ParametersGrid.addWidget(Slider, Row, 1)
        
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
        self.ParametersGrid.addWidget(SpinBox, Row, 2)
        
        # Connect signals
        if IsInteger:
            Slider.valueChanged.connect(SpinBox.setValue)
            SpinBox.valueChanged.connect(Slider.setValue)
        else:
            Slider.valueChanged.connect(lambda v: SpinBox.setValue(v / 100))
            SpinBox.valueChanged.connect(lambda v: Slider.setValue(int(v * 100)))
