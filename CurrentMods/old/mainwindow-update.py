# This is a partial implementation showing the changes needed to MainWindow.py

# Update the __init__ method to accept the StateManager parameter
def __init__(self, Config, StateManager):
    """
    Initialize the main window.
    
    Args:
        Config: Configuration manager instance
        StateManager: Parameter state manager instance
    """
    super().__init__()
    
    # Initialize logging
    self.Logger = logging.getLogger('OllamaModelEditor.MainWindow')
    
    # Store configuration and state manager
    self.Config = Config
    self.StateManager = StateManager
    
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

# Update the _CreateCentralWidget method to pass StateManager to ParameterEditor and BenchmarkView
def _CreateCentralWidget(self):
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
    
    # Add parameter editor tab - Pass StateManager to ParameterEditor
    self.ParameterEditorWidget = ParameterEditor(self.ModelManager, self.Config, self.StateManager)
    self.ParameterEditorWidget.SetStatusBar(self.StatusBar)  # Pass StatusBar reference
    self.TabWidget.addTab(self.ParameterEditorWidget, "Parameter Editor")
    
    # Add benchmark tab - Pass StateManager to BenchmarkView 
    self.BenchmarkWidget = BenchmarkView(self.ModelManager, self.Config, self.StateManager)
    self.TabWidget.addTab(self.BenchmarkWidget, "Benchmark")
    
    # Add analysis tab if available
    try:
        from GUI.Components.AnalysisView import AnalysisView
        self.AnalysisWidget = AnalysisView(self.ModelManager, self.Config)
        self.TabWidget.addTab(self.AnalysisWidget, "Analysis")
    except ImportError:
        # Analysis view not available, skip
        pass
