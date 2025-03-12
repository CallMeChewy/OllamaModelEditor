# File: ModelSelector.py
# Path: OllamaModelEditor/GUI/Components/ModelSelector.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Model selection component for the OllamaModelEditor application

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PySide6.QtCore import Signal, Slot

class ModelSelector(QWidget):
    """Widget for selecting Ollama models."""
    
    # Signal emitted when a model is selected
    ModelSelected = Signal(str)
    
    def __init__(self, ModelManager, Config):
        """
        Initialize the model selector.
        
        Args:
            ModelManager: Model manager instance
            Config: Configuration manager instance
        """
        super().__init__()
        
        # Store references
        self.ModelManager = ModelManager
        self.Config = Config
        
        # Set up UI
        self._SetupUI()
    
    def _SetupUI(self):
        """Set up the user interface."""
        # Create layout
        Layout = QVBoxLayout()
        self.setLayout(Layout)
        
        # Add header label
        HeaderLabel = QLabel("Available Models:")
        Layout.addWidget(HeaderLabel)
        
        # Add list widget
        self.ModelList = QListWidget()
        self.ModelList.currentTextChanged.connect(self._OnModelSelected)
        Layout.addWidget(self.ModelList)
        
        # Load models
        self._LoadModels()
    
    def _LoadModels(self):
        """Load available models."""
        # Clear list
        self.ModelList.clear()
        
        # Get available models
        Models = self.ModelManager.GetAvailableModels()
        
        # Add to list
        for Model in Models:
            self.ModelList.addItem(Model.get('name', 'Unknown'))
    
    @Slot(str)
    def _OnModelSelected(self, ModelName):
        """
        Handle model selection.
        
        Args:
            ModelName: Selected model name
        """
        if ModelName:
            # Emit signal
            self.ModelSelected.emit(ModelName)
