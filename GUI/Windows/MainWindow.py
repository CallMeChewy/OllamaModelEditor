# Updates for MainWindow.py to fix issues and enhance UI

# 1. Add objectNames to fix the saveState warnings
self.ModelSelectorDock.setObjectName("ModelLibraryDock")
self.MainToolbar.setObjectName("MainToolbar")

# 2. Add visual separation between menu and tabs
# Apply stylesheet to menu bar for better contrast
self.MenuBar.setStyleSheet("""
    QMenuBar {
        background-color: #2D2D2D;
        color: #FFFFFF;
        border-bottom: 1px solid #3D3D3D;
    }
    QMenuBar::item {
        background-color: transparent;
        padding: 6px 10px;
    }
    QMenuBar::item:selected {
        background-color: #3D3D3D;
        color: #FFFFFF;
    }
""")

# 3. Fix sidebar behavior - update _CreateDockWidgets method
def _CreateDockWidgets(self) -> None:
    """Create dock widgets."""
    # Model selector dock
    self.ModelSelectorDock = QDockWidget("Model Library", self)
    self.ModelSelectorDock.setObjectName("ModelLibraryDock")
    self.ModelSelectorDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    self.ModelSelectorDock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
    
    # Create a container widget with layout for the dock
    DockContainer = QWidget()
    DockLayout = QVBoxLayout(DockContainer)
    DockLayout.setContentsMargins(0, 0, 0, 0)
    
    # Add header with label and toolbar
    HeaderLayout = QHBoxLayout()
    HeaderLayout.setSpacing(2)
    HeaderLabel = QLabel("Available Models:")
    HeaderLabel.setStyleSheet("font-weight: bold;")
    HeaderLayout.addWidget(HeaderLabel)
    
    # Add spacer to push toolbar to right
    HeaderLayout.addStretch()
    
    # Add refresh button to dock header
    RefreshButton = QPushButton("↻")
    RefreshButton.setToolTip("Refresh Models")
    RefreshButton.setMaximumWidth(24)
    RefreshButton.clicked.connect(self._OnRefreshModels)
    HeaderLayout.addWidget(RefreshButton)
    
    DockLayout.addLayout(HeaderLayout)
    
    # Create model selector widget
    self.ModelSelectorWidget = ModelSelector(self.ModelManager, self.Config)
    DockLayout.addWidget(self.ModelSelectorWidget)
    
    # Set dock widget content
    self.ModelSelectorDock.setWidget(DockContainer)
    
    # Add dock to main window
    self.addDockWidget(Qt.LeftDockWidgetArea, self.ModelSelectorDock)
    self.ViewMenu.addAction(self.ModelSelectorDock.toggleViewAction())

# 4. Enhanced parameter editor - update method in ParameterEditor.py
def _SetupUI(self):
    """Set up the user interface."""
    # Create layout
    Layout = QVBoxLayout()
    self.setLayout(Layout)
    
    # Add header label
    HeaderLabel = QLabel("Model Parameters:")
    HeaderLabel.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
    Layout.addWidget(HeaderLabel)
    
    # Add parameter description
    DescriptionLabel = QLabel("Adjust these parameters to control the model's behavior and output:")
    DescriptionLabel.setWordWrap(True)
    Layout.addWidget(DescriptionLabel)
    
    # Create parameters grid
    self.ParametersGrid = QGridLayout()
    self.ParametersGrid.setColumnStretch(1, 1)  # Make slider column stretch
    self.ParametersGrid.setColumnMinimumWidth(0, 120)  # Fixed width for labels
    Layout.addLayout(self.ParametersGrid)
    
    # Add preset selector
    PresetLayout = QHBoxLayout()
    PresetLabel = QLabel("Presets:")
    self.PresetCombo = QComboBox()
    self.PresetCombo.addItems(["Default", "Creative", "Precise", "Fast", "Custom"])
    self.PresetCombo.currentTextChanged.connect(self._OnPresetChanged)
    PresetLayout.addWidget(PresetLabel)
    PresetLayout.addWidget(self.PresetCombo)
    PresetLayout.addStretch()
    
    # Add save preset button
    self.SavePresetButton = QPushButton("Save as Preset")
    self.SavePresetButton.clicked.connect(self._OnSavePreset)
    PresetLayout.addWidget(self.SavePresetButton)
    
    Layout.addLayout(PresetLayout)
    
    # Add parameter guidance section
    GuidanceFrame = QFrame()
    GuidanceFrame.setFrameShape(QFrame.StyledPanel)
    GuidanceFrame.setStyleSheet("background-color: rgba(80, 80, 80, 50); border-radius: 5px; padding: 10px;")
    GuidanceLayout = QVBoxLayout(GuidanceFrame)
    
    GuidanceTitle = QLabel("Parameter Guidance:")
    GuidanceTitle.setStyleSheet("font-weight: bold;")
    GuidanceLayout.addWidget(GuidanceTitle)
    
    self.GuidanceText = QLabel()
    self.GuidanceText.setWordWrap(True)
    self.GuidanceText.setText(
        "<b>Temperature:</b> Controls randomness. Higher values (0.7-1.0) produce more creative outputs, "
        "while lower values (0.2-0.5) make output more focused and deterministic.<br><br>"
        "<b>Top-P:</b> Controls diversity via nucleus sampling. Lower values make output more focused on likely tokens. "
        "0.9 is a good starting point.<br><br>"
        "<b>Max Tokens:</b> The maximum length of the generated text. Higher values allow for longer responses "
        "but consume more resources."
    )
    GuidanceLayout.addWidget(self.GuidanceText)
    
    Layout.addWidget(GuidanceFrame)
    
    # Add placeholder message
    self.PlaceholderLabel = QLabel("Select a model to edit parameters")
    self.PlaceholderLabel.setAlignment(Qt.AlignCenter)
    self.PlaceholderLabel.setStyleSheet("font-size: 14px; color: #888888;")
    Layout.addWidget(self.PlaceholderLabel)
    
    # Add stretch to bottom
    Layout.addStretch()

# Additional method for ParameterEditor.py
def _OnPresetChanged(self, PresetName):
    """
    Handle preset selection.
    
    Args:
        PresetName: Name of the selected preset
    """
    if not self.CurrentModel or PresetName == "Custom":
        return
    
    # Define preset values
    Presets = {
        "Default": {
            'Temperature': 0.7,
            'TopP': 0.9,
            'MaxTokens': 2048
        },
        "Creative": {
            'Temperature': 1.0,
            'TopP': 0.95,
            'MaxTokens': 4096
        },
        "Precise": {
            'Temperature': 0.3,
            'TopP': 0.7,
            'MaxTokens': 2048
        },
        "Fast": {
            'Temperature': 0.7,
            'TopP': 0.9,
            'MaxTokens': 1024
        }
    }
    
    # Apply preset
    if PresetName in Presets:
        Preset = Presets[PresetName]
        
        # Update UI without triggering updates
        self._UpdatingUI = True
        
        # Clear parameters grid
        while self.ParametersGrid.count():
            Item = self.ParametersGrid.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
        
        # Add parameter controls with preset values
        self._AddParameterControl("Temperature", Preset.get('Temperature', 0.7), 0.0, 2.0, 0.1)
        self._AddParameterControl("TopP", Preset.get('TopP', 0.9), 0.0, 1.0, 0.01)
        self._AddParameterControl("MaxTokens", Preset.get('MaxTokens', 2048), 1, 32000, 1, True)
        
        self._UpdatingUI = False
        
        # Save preset to model configuration
        self.ModelManager.UpdateModelParameters(self.CurrentModel, Preset)

def _OnSavePreset(self):
    """Handle save preset button click."""
    if not self.CurrentModel:
        return
    
    # Get current parameter values
    # Implementation would save current settings as a named preset
    QMessageBox.information(self, "Save Preset", "Preset saving functionality not yet implemented.")
