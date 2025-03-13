# File: BenchmarkView.py
# Path: OllamaModelEditor/GUI/Components/BenchmarkView.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-13
# Description: Benchmarking component with backward compatibility for the OllamaModelEditor application

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, 
    QFormLayout, QSpinBox, QCheckBox, QTabWidget, QApplication, QFileDialog,
    QFrame, QGridLayout, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon
import json
import time
from datetime import datetime

class BenchmarkView(QWidget):
    """Widget for benchmarking models with backward compatibility for StateManager."""
    
    def __init__(self, ModelManager, Config, StateManager=None):
        """
        Initialize the benchmark view.
        
        Args:
            ModelManager: Model manager instance
            Config: Configuration manager instance
            StateManager: Optional parameter state manager instance
        """
        super().__init__()
        
        # Store references
        self.ModelManager = ModelManager
        self.Config = Config
        self.StateManager = StateManager
        
        # Current benchmark results
        self.CurrentResults = None
        
        # Running benchmark flag
        self.IsRunning = False
        
        # Set up UI
        self._SetupUI()
    
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
        
        # Add model state view button if StateManager is available
        if self.StateManager:
            self.ViewStateButton = QPushButton("View Current Model State")
            self.ViewStateButton.clicked.connect(self._OnViewModelState)
            ConfigLayout.addRow(self.ViewStateButton)
        
        # Add benchmark type selector
        BenchmarkTypeLayout = QHBoxLayout()
        BenchmarkTypeLabel = QLabel("Benchmark Type:")
        self.BenchmarkTypeCombo = QComboBox()
        self.BenchmarkTypeCombo.addItems(["Standard", "Comparison", "Stress Test"])
        self.BenchmarkTypeCombo.currentTextChanged.connect(self._OnBenchmarkTypeChanged)
        BenchmarkTypeLayout.addWidget(BenchmarkTypeLabel)
        BenchmarkTypeLayout.addWidget(self.BenchmarkTypeCombo)
        ConfigLayout.addRow(BenchmarkTypeLayout)
        
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
        