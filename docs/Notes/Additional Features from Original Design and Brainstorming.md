# Additional Features from Original Design and Brainstorming

# 1. Add benchmark functionality to BenchmarkView.py

# Update BenchmarkView._SetupUI method
def _SetupUI(self):
    """Set up the user interface."""
    # Create layout
    Layout = QVBoxLayout()
    self.setLayout(Layout)
    
    # Add header label
    HeaderLabel = QLabel("Model Benchmark")
    HeaderLabel.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
    Layout.addWidget(HeaderLabel)
    
    # Add description
    DescriptionLabel = QLabel(
        "Compare model performance with different configurations. "
        "Enter sample prompts below to test how the model responds with current settings."
    )
    DescriptionLabel.setWordWrap(True)
    Layout.addWidget(DescriptionLabel)
    
    # Add benchmark configuration section
    ConfigFrame = QFrame()
    ConfigFrame.setFrameShape(QFrame.StyledPanel)
    ConfigLayout = QFormLayout(ConfigFrame)
    
    # Add model comparison selector
    self.CompareCheckbox = QCheckBox("Compare with another configuration")
    self.CompareCheckbox.toggled.connect(self._OnCompareToggled)
    ConfigLayout.addRow(self.CompareCheckbox)
    
    # Add comparison config selector (initially hidden)
    self.ComparisonConfigLayout = QHBoxLayout()
    self.ComparisonConfigLabel = QLabel("Comparison config:")
    self.ComparisonConfigLabel.setEnabled(False)
    self.ComparisonConfigCombo = QComboBox()
    self.ComparisonConfigCombo.setEnabled(False)
    self.ComparisonConfigCombo.addItems(["Default", "Creative", "Precise", "Fast", "Custom..."])
    self.ComparisonConfigLayout.addWidget(self.ComparisonConfigLabel)
    self.ComparisonConfigLayout.addWidget(self.ComparisonConfigCombo, 1)
    ConfigLayout.addRow(self.ComparisonConfigLayout)
    
    # Add repetition control
    RepetitionLayout = QHBoxLayout()
    self.RepetitionLabel = QLabel("Repetitions:")
    self.RepetitionSpinner = QSpinBox()
    self.RepetitionSpinner.setMinimum(1)
    self.RepetitionSpinner.setMaximum(10)
    self.RepetitionSpinner.setValue(3)
    self.RepetitionSpinner.setToolTip("Number of times to run each prompt for more accurate benchmarking")
    RepetitionLayout.addWidget(self.RepetitionLabel)
    RepetitionLayout.addWidget(self.RepetitionSpinner)
    RepetitionLayout.addStretch()
    ConfigLayout.addRow(RepetitionLayout)
    
    Layout.addWidget(ConfigFrame)
    
    # Add prompt input
    PromptLabel = QLabel("Enter benchmark prompts (one per line):")
    Layout.addWidget(PromptLabel)
    
    self.PromptsText = QTextEdit()
    self.PromptsText.setPlaceholderText("Enter benchmark prompts here...\n\nExample:\nSummarize the key features of neural networks.\nExplain the difference between supervised and unsupervised learning.\nWrite a short poem about artificial intelligence.")
    self.PromptsText.setMinimumHeight(100)
    Layout.addWidget(self.PromptsText)
    
    # Add buttons
    ButtonLayout = QHBoxLayout()
    
    self.RunButton = QPushButton("Run Benchmark")
    self.RunButton.setIcon(QIcon.fromTheme("media-playback-start"))
    self.RunButton.clicked.connect(self._OnRunBenchmark)
    ButtonLayout.addWidget(self.RunButton)
    
    self.StopButton = QPushButton("Stop")
    self.StopButton.setIcon(QIcon.fromTheme("media-playback-stop"))
    self.StopButton.clicked.connect(self._OnStopBenchmark)
    self.StopButton.setEnabled(False)
    ButtonLayout.addWidget(self.StopButton)
    
    self.SaveButton = QPushButton("Save Results")
    self.SaveButton.setIcon(QIcon.fromTheme("document-save"))
    self.SaveButton.clicked.connect(self._OnSaveResults)
    self.SaveButton.setEnabled(False)
    ButtonLayout.addWidget(self.SaveButton)
    
    Layout.addLayout(ButtonLayout)
    
    # Add results display with tabs
    self.ResultsTabs = QTabWidget()
    
    # Summary tab
    self.SummaryTab = QWidget()
    SummaryLayout = QVBoxLayout(self.SummaryTab)
    
    self.SummaryText = QTextEdit()
    self.SummaryText.setReadOnly(True)
    SummaryLayout.addWidget(self.SummaryText)
    
    # Charts tab
    self.ChartsTab = QWidget()
    ChartsLayout = QVBoxLayout(self.ChartsTab)
    
    self.ChartPlaceholder = QLabel("Charts will appear here after running benchmarks")
    self.ChartPlaceholder.setAlignment(Qt.AlignCenter)
    ChartsLayout.addWidget(self.ChartPlaceholder)
    
    # Detailed results tab
    self.DetailsTab = QWidget()
    DetailsLayout = QVBoxLayout(self.DetailsTab)
    
    self.DetailsText = QTextEdit()
    self.DetailsText.setReadOnly(True)
    DetailsLayout.addWidget(self.DetailsText)
    
    # Add tabs to tab widget
    self.ResultsTabs.addTab(self.SummaryTab, "Summary")
    self.ResultsTabs.addTab(self.ChartsTab, "Charts")
    self.ResultsTabs.addTab(self.DetailsTab, "Details")
    
    Layout.addWidget(self.ResultsTabs)

# Add new method to BenchmarkView
def _OnCompareToggled(self, Checked):
    """
    Handle compare checkbox toggle.
    
    Args:
        Checked: Whether the checkbox is checked
    """
    self.ComparisonConfigLabel.setEnabled(Checked)
    self.ComparisonConfigCombo.setEnabled(Checked)

# 2. Add configuration export/import functionality to MainWindow.py

# Add to MainWindow._OnExportModel
def _OnExportModel(self) -> None:
    """Handle export model definition action."""
    CurrentModel = self.ModelManager.GetCurrentModel()
    if not CurrentModel:
        QMessageBox.warning(
            self,
            "Export Error",
            "Please select a model first."
        )
        return
    
    ModelName = CurrentModel.get('name', 'unknown')
    
    # Get save file path
    FilePath, _ = QFileDialog.getSaveFileName(
        self,
        "Export Model Configuration",
        f"{ModelName}_config.json",
        "JSON Files (*.json);;YAML Files (*.yaml *.yml);;All Files (*.*)"
    )
    
    if not FilePath:
        return
    
    # Export model definition
    Success = self.ModelManager.ExportModelDefinition(ModelName, FilePath)
    
    if Success:
        QMessageBox.information(
            self,
            "Export Successful",
            f"Model configuration for {ModelName} was exported successfully to {FilePath}."
        )
    else:
        QMessageBox.critical(
            self,
            "Export Error",
            f"Failed to export model configuration for {ModelName}."
        )

# Add export configuration dialog
class ExportConfigDialog(QDialog):
    """Dialog for exporting model configuration."""
    
    def __init__(self, ModelName, Config, Parent=None):
        """
        Initialize the dialog.
        
        Args:
            ModelName: Name of the model
            Config: Configuration manager instance
            Parent: Parent widget
        """
        super().__init__(Parent)
        
        self.ModelName = ModelName
        self.Config = Config
        
        self.setWindowTitle(f"Export {ModelName} Configuration")
        self.setMinimumWidth(400)
        
        # Create layout
        Layout = QVBoxLayout(self)
        
        # Add export options
        OptionsGroup = QGroupBox("Export Options")
        OptionsLayout = QVBoxLayout(OptionsGroup)
        
        self.IncludeModelInfo = QCheckBox("Include Model Information")
        self.IncludeModelInfo.setChecked(True)
        OptionsLayout.addWidget(self.IncludeModelInfo)
        
        self.IncludeParameters = QCheckBox("Include Parameters")
        self.IncludeParameters.setChecked(True)
        OptionsLayout.addWidget(self.IncludeParameters)
        
        self.IncludeBenchmarks = QCheckBox("Include Benchmark Results")
        self.IncludeBenchmarks.setChecked(False)
        OptionsLayout.addWidget(self.IncludeBenchmarks)
        
        Layout.addWidget(OptionsGroup)
        
        # Add file format selection
        FormatGroup = QGroupBox("File Format")
        FormatLayout = QVBoxLayout(FormatGroup)
        
        self.JsonFormat = QRadioButton("JSON")
        self.JsonFormat.setChecked(True)
        FormatLayout.addWidget(self.JsonFormat)
        
        self.YamlFormat = QRadioButton("YAML")
        FormatLayout.addWidget(self.YamlFormat)
        
        Layout.addWidget(FormatGroup)
        
        # Add buttons
        ButtonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ButtonBox.accepted.connect(self.accept)
        ButtonBox.rejected.connect(self.reject)
        Layout.addWidget(ButtonBox)

# 3. Add detailed analysis view

# Create new AnalysisView.py component
"""
# File: AnalysisView.py
# Path: OllamaModelEditor/GUI/Components/AnalysisView.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-12
# Last Modified: 2025-03-12
# Description: Detailed analysis component for the OllamaModelEditor application

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QComboBox, QSplitter, QTabWidget, QFrame,
    QFormLayout, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

class AnalysisView(QWidget):
    \"""Widget for detailed model analysis.\"""
    
    def __init__(self, ModelManager, Config):
        \"""
        Initialize the analysis view.
        
        Args:
            ModelManager: Model manager instance
            Config: Configuration manager instance
        \"""
        super().__init__()
        
        # Store references
        self.ModelManager = ModelManager
        self.Config = Config
        
        # Set up UI
        self._SetupUI()
    
    def _SetupUI(self):
        \"""Set up the user interface.\"""
        # Create layout
        Layout = QVBoxLayout()
        self.setLayout(Layout)
        
        # Add header label
        HeaderLabel = QLabel("Detailed Analysis")
        HeaderLabel.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        Layout.addWidget(HeaderLabel)
        
        # Add description
        DescriptionLabel = QLabel(
            "Get detailed insights into how parameter changes affect model performance. "
            "Test with different inputs and analyze the outputs."
        )
        DescriptionLabel.setWordWrap(True)
        Layout.addWidget(DescriptionLabel)
        
        # Create main splitter
        Splitter = QSplitter(Qt.Vertical)
        Splitter.setHandleWidth(6)
        Splitter.setChildrenCollapsible(False)
        
        # Input section
        InputWidget = QWidget()
        InputLayout = QVBoxLayout(InputWidget)
        InputLayout.setContentsMargins(0, 0, 0, 0)
        
        # Input parameters
        InputParamsLayout = QHBoxLayout()
        
        # Input type selector
        InputTypeLayout = QFormLayout()
        self.InputTypeCombo = QComboBox()
        self.InputTypeCombo.addItems(["Text", "Code", "Summary", "Translation", "Question/Answer"])
        InputTypeLayout.addRow("Input Type:", self.InputTypeCombo)
        InputParamsLayout.addLayout(InputTypeLayout)
        
        # Max tokens
        MaxTokensLayout = QFormLayout()
        self.MaxTokensSpinner = QSpinBox()
        self.MaxTokensSpinner.setRange(1, 32000)
        self.MaxTokensSpinner.setValue(2048)
        MaxTokensLayout.addRow("Max Tokens:", self.MaxTokensSpinner)
        InputParamsLayout.addLayout(MaxTokensLayout)
        
        # Stream output
        StreamLayout = QFormLayout()
        self.StreamCheckbox = QCheckBox("Stream Output")
        self.StreamCheckbox.setChecked(True)
        StreamLayout.addRow(self.StreamCheckbox)
        InputParamsLayout.addLayout(StreamLayout)
        
        InputLayout.addLayout(InputParamsLayout)
        
        # Input text
        InputLabel = QLabel("Input:")
        InputLayout.addWidget(InputLabel)
        
        self.InputText = QTextEdit()
        self.InputText.setPlaceholderText("Enter your input text here...")
        self.InputText.setMinimumHeight(100)
        InputLayout.addWidget(self.InputText)
        
        # Action buttons
        ButtonLayout = QHBoxLayout()
        
        self.AnalyzeButton = QPushButton("Analyze")
        self.AnalyzeButton.clicked.connect(self._OnAnalyze)
        ButtonLayout.addWidget(self.AnalyzeButton)
        
        self.ClearButton = QPushButton("Clear")
        self.ClearButton.clicked.connect(self._OnClear)
        ButtonLayout.addWidget(self.ClearButton)
        
        InputLayout.addLayout(ButtonLayout)
        
        # Add input widget to splitter
        Splitter.addWidget(InputWidget)
        
        # Results section
        ResultsWidget = QWidget()
        ResultsLayout = QVBoxLayout(ResultsWidget)
        ResultsLayout.setContentsMargins(0, 0, 0, 0)
        
        # Results tabs
        self.ResultsTabs = QTabWidget()
        
        # Output tab
        self.OutputTab = QWidget()
        OutputLayout = QVBoxLayout(self.OutputTab)
        
        self.OutputText = QTextEdit()
        self.OutputText.setReadOnly(True)
        OutputLayout.addWidget(self.OutputText)
        
        # Analysis tab
        self.AnalysisTab = QWidget()
        AnalysisLayout = QVBoxLayout(self.AnalysisTab)
        
        self.AnalysisText = QTextEdit()
        self.AnalysisText.setReadOnly(True)
        AnalysisLayout.addWidget(self.AnalysisText)
        
        # Metrics tab
        self.MetricsTab = QWidget()
        MetricsLayout = QVBoxLayout(self.MetricsTab)
        
        self.MetricsText = QTextEdit()
        self.MetricsText.setReadOnly(True)
        MetricsLayout.addWidget(self.MetricsText)
        
        # Add tabs to tab widget
        self.ResultsTabs.addTab(self.OutputTab, "Output")
        self.ResultsTabs.addTab(self.AnalysisTab, "Analysis")
        self.ResultsTabs.addTab(self.MetricsTab, "Metrics")
        
        ResultsLayout.addWidget(self.ResultsTabs)
        
        # Add results widget to splitter
        Splitter.addWidget(ResultsWidget)
        
        # Set initial splitter sizes
        Splitter.