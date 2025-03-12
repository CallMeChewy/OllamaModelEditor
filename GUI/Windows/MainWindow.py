# File: MainWindow.py
# Path: OllamaModelEditor/GUI/Windows/MainWindow.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Main window for the OllamaModelEditor application

import sys
from pathlib import Path
import logging
from typing import Optional, Dict, Any

# Import PySide6 components
from PySide6.QtWidgets import (
    QMainWindow, QAction, QMenu, QToolBar, QStatusBar, 
    QVBoxLayout, QHBoxLayout, QWidget, QTabWidget,
    QComboBox, QLabel, QPushButton, QMessageBox,
    QSplitter, QDockWidget
)
from PySide6.QtCore import Qt, QSize, Slot, Signal, QTimer
from PySide6.QtGui import QIcon, QFont, QKeySequence

# Import project modules
from Core.ConfigManager import ConfigManager
from Core.ModelManager import ModelManager
from GUI.Components.ModelSelector import ModelSelector
from GUI.Components.ParameterEditor import ParameterEditor
from GUI.Components.BenchmarkView import BenchmarkView

class MainWindow(QMainWindow):
    """Main application window for OllamaModelEditor."""
    
    def __init__(self, Config: ConfigManager):
        """
        Initialize the main window.
        
        Args:
            Config: Configuration manager instance
        """
        super().__init__()
        
        # Initialize logging
        self.Logger = logging.getLogger('OllamaModelEditor.MainWindow')
        
        # Store configuration
        self.Config = Config
        
        # Create model manager
        self.ModelManager = ModelManager(Config)
        
        # Set up UI
        self._SetupWindow()
        self._CreateMenus()
        self._CreateToolbars()
        self._CreateStatusBar()
        self._CreateCentralWidget()
        self._CreateDockWidgets()
        
        # Load user preferences
        self._LoadPreferences()
        
        # Connect signals and slots
        self._ConnectSignals()
        
        # Load models
        self._LoadModels()
    
    def _SetupWindow(self) -> None:
        """Set up the main window properties."""
        # Set window title and icon
        self.setWindowTitle("Ollama Model Editor")
        # self.setWindowIcon(QIcon("GUI/Assets/icons/app_icon.png"))
        
        # Set window geometry
        WindowWidth = self.Config.GetUserPreference('WindowWidth', 1200)
        WindowHeight = self.Config.GetUserPreference('WindowHeight', 800)
        self.resize(WindowWidth, WindowHeight)
        
        # Get the screen size
        ScreenSize = self.screen().size()
        
        # Center window on screen
        self.move(
            (ScreenSize.width() - WindowWidth) // 2,
            (ScreenSize.height() - WindowHeight) // 2
        )
    
    def _CreateMenus(self) -> None:
        """Create the application menu bar."""
        self.MenuBar = self.menuBar()
        
        # File menu
        self.FileMenu = self.MenuBar.addMenu("&File")
        
        self.NewAction = QAction("&New Configuration", self)
        self.NewAction.setShortcut(QKeySequence.New)
        self.NewAction.triggered.connect(self._OnNewConfig)
        self.FileMenu.addAction(self.NewAction)
        
        self.OpenAction = QAction("&Open Configuration...", self)
        self.OpenAction.setShortcut(QKeySequence.Open)
        self.OpenAction.triggered.connect(self._OnOpenConfig)
        self.FileMenu.addAction(self.OpenAction)
        
        self.SaveAction = QAction("&Save Configuration", self)
        self.SaveAction.setShortcut(QKeySequence.Save)
        self.SaveAction.triggered.connect(self._OnSaveConfig)
        self.FileMenu.addAction(self.SaveAction)
        
        self.SaveAsAction = QAction("Save Configuration &As...", self)
        self.SaveAsAction.setShortcut(QKeySequence.SaveAs)
        self.SaveAsAction.triggered.connect(self._OnSaveConfigAs)
        self.FileMenu.addAction(self.SaveAsAction)
        
        self.FileMenu.addSeparator()
        
        self.ExitAction = QAction("E&xit", self)
        self.ExitAction.setShortcut(QKeySequence.Quit)
        self.ExitAction.triggered.connect(self.close)
        self.FileMenu.addAction(self.ExitAction)
        
        # Edit menu
        self.EditMenu = self.MenuBar.addMenu("&Edit")
        
        self.PreferencesAction = QAction("&Preferences...", self)
        self.PreferencesAction.triggered.connect(self._OnPreferences)
        self.EditMenu.addAction(self.PreferencesAction)
        
        # View menu
        self.ViewMenu = self.MenuBar.addMenu("&View")
        
        # Tools menu
        self.ToolsMenu = self.MenuBar.addMenu("&Tools")
        
        self.BenchmarkAction = QAction("&Benchmark Model...", self)
        self.BenchmarkAction.triggered.connect(self._OnBenchmark)
        self.ToolsMenu.addAction(self.BenchmarkAction)
        
        self.ExportAction = QAction("&Export Model Definition...", self)
        self.ExportAction.triggered.connect(self._OnExportModel)
        self.ToolsMenu.addAction(self.ExportAction)
        
        # Help menu
        self.HelpMenu = self.MenuBar.addMenu("&Help")
        
        self.DocumentationAction = QAction("&Documentation", self)
        self.DocumentationAction.triggered.connect(self._OnDocumentation)
        self.HelpMenu.addAction(self.DocumentationAction)
        
        self.HelpMenu.addSeparator()
        
        self.AboutAction = QAction("&About", self)
        self.AboutAction.triggered.connect(self._OnAbout)
        self.HelpMenu.addAction(self.AboutAction)
    
    def _CreateToolbars(self) -> None:
        """Create the application toolbars."""
        # Main toolbar
        self.MainToolbar = QToolBar("Main Toolbar")
        self.MainToolbar.setMovable(False)
        self.MainToolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.MainToolbar)
        
        # Add actions to toolbar
        self.MainToolbar.addAction(self.NewAction)
        self.MainToolbar.addAction(self.OpenAction)
        self.MainToolbar.addAction(self.SaveAction)
        self.MainToolbar.addSeparator()
        
        # Add model selector to toolbar
        self.ModelSelectorLabel = QLabel("Model:")
        self.MainToolbar.addWidget(self.ModelSelectorLabel)
        
        self.ModelSelectorCombo = QComboBox()
        self.ModelSelectorCombo.setMinimumWidth(200)
        self.MainToolbar.addWidget(self.ModelSelectorCombo)
        
        self.RefreshModelsButton = QPushButton("Refresh")
        self.RefreshModelsButton.clicked.connect(self._OnRefreshModels)
        self.MainToolbar.addWidget(self.RefreshModelsButton)
    
    def _CreateStatusBar(self) -> None:
        """Create the application status bar."""
        self.StatusBar = QStatusBar()
        self.setStatusBar(self.StatusBar)
        
        # Add status labels
        self.ModelStatusLabel = QLabel("No model selected")
        self.StatusBar.addWidget(self.ModelStatusLabel)
        
        self.APIStatusLabel = QLabel("API: Not connected")
        self.StatusBar.addPermanentWidget(self.APIStatusLabel)
    
    def _CreateCentralWidget(self) -> None:
        """Create the central widget."""
        # Create central widget
        self.CentralWidget = QWidget()
        self.setCentralWidget(self.CentralWidget)
        
        # Main layout
        self.MainLayout = QVBoxLayout()
        self.CentralWidget.setLayout(self.MainLayout)
        
        # Create tab widget
        self.TabWidget = QTabWidget()
        self.MainLayout.addWidget(self.TabWidget)
        
        # Add parameter editor tab
        self.ParameterEditorWidget = ParameterEditor(self.ModelManager, self.Config)
        self.TabWidget.addTab(self.ParameterEditorWidget, "Parameter Editor")
        
        # Add benchmark tab
        self.BenchmarkWidget = BenchmarkView(self.ModelManager, self.Config)
        self.TabWidget.addTab(self.BenchmarkWidget, "Benchmark")
    
    def _CreateDockWidgets(self) -> None:
        """Create dock widgets."""
        # Model selector dock
        self.ModelSelectorDock = QDockWidget("Model Library", self)
        self.ModelSelectorDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.ModelSelectorWidget = ModelSelector(self.ModelManager, self.Config)
        self.ModelSelectorDock.setWidget(self.ModelSelectorWidget)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.ModelSelectorDock)
        self.ViewMenu.addAction(self.ModelSelectorDock.toggleViewAction())
    
    def _LoadPreferences(self) -> None:
        """Load user preferences."""
        # Load window state if saved
        WindowState = self.Config.GetUserPreference('WindowState')
        WindowGeometry = self.Config.GetUserPreference('WindowGeometry')
        
        if WindowState:
            self.restoreState(WindowState)
        
        if WindowGeometry:
            self.restoreGeometry(WindowGeometry)
        
        # Apply theme
        Theme = self.Config.GetUserPreference('Theme', 'system')
        self._ApplyTheme(Theme)
    
    def _ApplyTheme(self, Theme: str) -> None:
        """
        Apply the selected theme.
        
        Args:
            Theme: Theme name ('light', 'dark', or 'system')
        """
        # Theme implementation would go here
        pass
    
    def _ConnectSignals(self) -> None:
        """Connect signals and slots."""
        # Connect model selector combo box
        self.ModelSelectorCombo.currentTextChanged.connect(self._OnModelSelected)
        
        # Connect model selector widget
        self.ModelSelectorWidget.ModelSelected.connect(self._OnModelSelectedFromWidget)
    
    def _LoadModels(self) -> None:
        """Load available models."""
        # Update status
        self.StatusBar.showMessage("Loading models...", 2000)
        
        # Get available models
        Models = self.ModelManager.GetAvailableModels()
        
        # Update model selector combo box
        self.ModelSelectorCombo.clear()
        for Model in Models:
            self.ModelSelectorCombo.addItem(Model.get('name', 'Unknown'))
        
        # Update status
        if Models:
            self.APIStatusLabel.setText("API: Connected")
            self.StatusBar.showMessage(f"Loaded {len(Models)} models", 3000)
        else:
            self.APIStatusLabel.setText("API: Error")
            self.StatusBar.showMessage("Failed to load models", 3000)
    
    @Slot()
    def _OnRefreshModels(self) -> None:
        """Handle refresh models button click."""
        self._LoadModels()
    
    @Slot(str)
    def _OnModelSelected(self, ModelName: str) -> None:
        """
        Handle model selection from combo box.
        
        Args:
            ModelName: Selected model name
        """
        if not ModelName:
            return
        
        # Set current model
        if self.ModelManager.SetCurrentModel(ModelName):
            self.ModelStatusLabel.setText(f"Model: {ModelName}")
            self.StatusBar.showMessage(f"Model {ModelName} selected", 3000)
            
            # Update parameter editor
            self.ParameterEditorWidget.LoadModel(ModelName)
        else:
            self.StatusBar.showMessage(f"Failed to select model {ModelName}", 3000)
    
    @Slot(str)
    def _OnModelSelectedFromWidget(self, ModelName: str) -> None:
        """
        Handle model selection from model selector widget.
        
        Args:
            ModelName: Selected model name
        """
        # Update combo box
        Index = self.ModelSelectorCombo.findText(ModelName)
        if Index >= 0:
            self.ModelSelectorCombo.setCurrentIndex(Index)
    
    @Slot()
    def _OnNewConfig(self) -> None:
        """Handle new configuration action."""
        # Check if current configuration should be saved
        # Implementation would go here
        
        # Create new configuration
        pass
    
    @Slot()
    def _OnOpenConfig(self) -> None:
        """Handle open configuration action."""
        # Implementation would go here
        pass
    
    @Slot()
    def _OnSaveConfig(self) -> None:
        """Handle save configuration action."""
        # Implementation would go here
        pass
    
    @Slot()
    def _OnSaveConfigAs(self) -> None:
        """Handle save configuration as action."""
        # Implementation would go here
        pass
    
    @Slot()
    def _OnPreferences(self) -> None:
        """Handle preferences action."""
        # Implementation would go here
        pass
    
    @Slot()
    def _OnBenchmark(self) -> None:
        """Handle benchmark action."""
        # Implementation would go here
        pass
    
    @Slot()
    def _OnExportModel(self) -> None:
        """Handle export model action."""
        # Implementation would go here
        pass
    
    @Slot()
    def _OnDocumentation(self) -> None:
        """Handle documentation action."""
        # Implementation would go here
        pass
    
    @Slot()
    def _OnAbout(self) -> None:
        """Handle about action."""
        AboutText = (
            "<h2>Ollama Model Editor</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A powerful tool for customizing and optimizing Ollama AI models.</p>"
            "<p>This project is a collaboration between human developers and AI assistants.</p>"
            "<p>&copy; 2025 Herbert J. Bowers (Herb@BowersWorld.com)</p>"
        )
        
        QMessageBox.about(self, "About Ollama Model Editor", AboutText)
    
    def closeEvent(self, event) -> None:
        """
        Handle window close event.
        
        Save user preferences before closing.
        """
        # Save window state and geometry
        self.Config.SetUserPreference('WindowState', self.saveState())
        self.Config.SetUserPreference('WindowGeometry', self.saveGeometry())
        self.Config.SetUserPreference('WindowWidth', self.width())
        self.Config.SetUserPreference('WindowHeight', self.height())
        
        # Save configuration
        self.Config.SaveConfig()
        
        # Accept close event
        event.accept()
