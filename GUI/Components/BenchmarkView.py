# File: BenchmarkView.py
# Path: OllamaModelEditor/GUI/Components/BenchmarkView.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-13
# Description: Enhanced benchmarking component with state tracking for the OllamaModelEditor application

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, 
    QFormLayout, QSpinBox, QCheckBox, QTabWidget, QApplication, QFileDialog,
    QFrame, QGridLayout, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QDialogButtonBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QFont, QColor
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

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
            
            self.StateTable.setItem(Row, 2, CurrItem)
            
            Row += 1

class BenchmarkView(QWidget):
    """Widget for benchmarking models with state tracking."""
    
    def __init__(self, ModelManager, Config, StateManager):
        """
        Initialize the benchmark view.
        
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
        
        # Add model state view button
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
        
        Layout.addWidget(self.ResultsTabs)
    
    def _OnBenchmarkTypeChanged(self, BenchmarkType):
        """
        Handle benchmark type change.
        
        Args:
            BenchmarkType: Selected benchmark type
        """
        # Enable/disable controls based on benchmark type
        if BenchmarkType == "Comparison":
            self.CompareCheckbox.setChecked(True)
            self.CompareCheckbox.setEnabled(False)
        elif BenchmarkType == "Stress Test":
            self.CompareCheckbox.setChecked(False)
            self.CompareCheckbox.setEnabled(False)
            
            # TODO: Add stress test specific controls
        else:  # Standard
            self.CompareCheckbox.setEnabled(True)
    
    def _OnViewModelState(self):
        """Handle view model state button click."""
        # Get current model
        CurrentModel = self.ModelManager.GetCurrentModel()
        if not CurrentModel:
            QMessageBox.warning(
                self,
                "No Model Selected",
                "Please select a model first."
            )
            return
        
        ModelName = CurrentModel.get('name')
        
        # Show model state dialog
        Dialog = ModelStateDialog(ModelName, self.StateManager, self)
        Dialog.exec()
    
    def _OnCompareToggled(self, Checked):
        """
        Handle compare checkbox toggle.
        
        Args:
            Checked: Whether the checkbox is checked
        """
        self.ComparisonConfigLabel.setEnabled(Checked)
        self.ComparisonConfigCombo.setEnabled(Checked)
    
    def _OnRunBenchmark(self):
        """Handle run benchmark button click."""
        # Get prompts
        PromptText = self.PromptsText.toPlainText()
        Prompts = [p.strip() for p in PromptText.split('\n') if p.strip()]
        
        if not Prompts:
            self.SummaryText.setText("Please enter at least one prompt.")
            return
        
        # Get current model
        CurrentModel = self.ModelManager.GetCurrentModel()
        if not CurrentModel:
            self.SummaryText.setText("Please select a model first.")
            return
        
        ModelName = CurrentModel.get('name')
        
        # Get benchmark repetitions
        Repetitions = self.RepetitionSpinner.value()
        
        # Get benchmark type
        BenchmarkType = self.BenchmarkTypeCombo.currentText()
        
        # Check if comparing configurations
        ComparisonConfig = None
        if BenchmarkType == "Comparison" or self.CompareCheckbox.isChecked():
            ComparisonConfigName = self.ComparisonConfigCombo.currentText()
            
            # Get configuration parameters
            if ComparisonConfigName == "Custom...":
                # TODO: Implement custom configuration dialog
                QMessageBox.information(
                    self,
                    "Not Implemented",
                    "Custom comparison configuration is not yet implemented."
                )
                return
            elif ComparisonConfigName in ["Default", "Creative", "Precise", "Fast"]:
                # Use built-in preset
                ComparisonConfig = self.ModelManager.GetPresetParameters(ComparisonConfigName)
        
        # Get current parameter state for reference
        CurrentState = self.StateManager.CurrentStates.get(ModelName, {})
        
        # Disable run button and enable stop button
        self.RunButton.setEnabled(False)
        self.StopButton.setEnabled(True)
        self.IsRunning = True
        
        # Update status
        self.SummaryText.setText(f"Running benchmark for {ModelName}...\n")
        self.SummaryText.append(f"Using the following parameters:\n")
        for Param, Value in CurrentState.items():
            self.SummaryText.append(f"  • {Param}: {Value}")
        self.SummaryText.append("\n")
        QApplication.processEvents()
        
        # Run benchmark
        Results = self.ModelManager.BenchmarkModel(ModelName, Prompts, Runs=Repetitions)
        
        # Set model state information in results
        Results["model_state"] = {
            "original": self.StateManager.OriginalStates.get(ModelName, {}),
            "current": CurrentState
        }
        
        # If comparing, run benchmark with comparison configuration
        if ComparisonConfig:
            self.SummaryText.append(f"Running comparison benchmark with {ComparisonConfigName} configuration...\n")
            self.SummaryText.append(f"Using the following parameters:\n")
            for Param, Value in ComparisonConfig.items():
                self.SummaryText.append(f"  • {Param}: {Value}")
            self.SummaryText.append("\n")
            QApplication.processEvents()
            
            ComparisonResults = self.ModelManager.BenchmarkModel(
                ModelName, 
                Prompts, 
                Parameters=ComparisonConfig,
                Runs=Repetitions
            )
            
            # Add comparison results
            Results["comparison"] = ComparisonResults
            Results["comparison_config_name"] = ComparisonConfigName
        
        # For stress test, add additional metrics
        if BenchmarkType == "Stress Test":
            # TODO: Implement stress test specific metrics
            pass
        
        # Enable run button and disable stop button
        self.RunButton.setEnabled(True)
        self.StopButton.setEnabled(False)
        self.IsRunning = False
        
        if "error" in Results:
            self.SummaryText.setText(f"Error running benchmark: {Results['error']}")
            return
        
        # Store current results
        self.CurrentResults = Results
        
        # Display summary results
        self._DisplayBenchmarkSummary(Results)
        
        # Create charts
        self._CreateBenchmarkCharts(Results)
        
        # Display detailed results
        self._DisplayBenchmarkDetails(Results)
        
        # Enable save button
        self.SaveButton.setEnabled(True)
    
    def _OnStopBenchmark(self):
        """Handle stop benchmark button click."""
        # Set flag to stop benchmark
        self.IsRunning = False
        
        # Update status
        self.SummaryText.append("Stopping benchmark...\n")
        
        # Enable run button and disable stop button
        self.RunButton.setEnabled(True)
        self.StopButton.setEnabled(False)
    
    def _DisplayBenchmarkSummary(self, Results):
        """
        Display benchmark summary.
        
        Args:
            Results: Benchmark results
        """
        Summary = Results.get('summary', {})
        Model = Results.get('model', 'Unknown')
        Parameters = Results.get('parameters', {})
        ModelState = Results.get('model_state', {})
        
        SummaryText = f"<h2>Benchmark Results for {Model}</h2>\n"
        
        # Add benchmark type
        BenchmarkType = self.BenchmarkTypeCombo.currentText()
        SummaryText += f"<p><b>Benchmark Type:</b> {BenchmarkType}</p>\n"
        
        # Add model state information
        SummaryText += "<h3>Model Parameters</h3>\n"
        
        # Create table for parameters with highlighting for changed values
        SummaryText += "<table border='1' cellpadding='4' cellspacing='0' style='border-collapse: collapse;'>\n"
        SummaryText += "<tr><th>Parameter</th><th>Original Value</th><th>Benchmark Value</th></tr>\n"
        
        # Get parameter differences
        OriginalState = ModelState.get('original', {})
        CurrentState = ModelState.get('current', {})
        
        # Show all parameters used in the benchmark
        for Param, Value in Parameters.items():
            OrigValue = OriginalState.get(Param, Value)
            
            # Check if value is different from original
            IsDifferent = OrigValue != Value
            
            # Create row with highlighting if different
            if IsDifferent:
                SummaryText += f"<tr><td>{Param}</td><td>{OrigValue}</td><td style='background-color: #FFFF99;'>{Value}</td></tr>\n"
            else:
                SummaryText += f"<tr><td>{Param}</td><td>{OrigValue}</td><td>{Value}</td></tr>\n"
        
        SummaryText += "</table>\n"
        
        # Add summary statistics
        SummaryText += "<h3>Summary Statistics</h3>\n<ul>"
        SummaryText += f"<li><b>Total Tests:</b> {Summary.get('total_tests', 0)}</li>"
        SummaryText += f"<li><b>Total Tokens:</b> {Summary.get('total_tokens', 0)}</li>"
        SummaryText += f"<li><b>Total Time:</b> {Summary.get('total_time', 0):.2f} seconds</li>"
        SummaryText += f"<li><b>Average Tokens/Second:</b> {Summary.get('average_tokens_per_second', 0):.2f}</li>"
        SummaryText += f"<li><b>Average Time/Test:</b> {Summary.get('average_time_per_test', 0):.2f} seconds</li>"
        SummaryText += f"<li><b>Benchmark Date:</b> {Summary.get('benchmark_date', 'Unknown')}</li>"
        SummaryText += "</ul>\n"
        
        # Add comparison results if available
        if "comparison" in Results:
            ComparisonResults = Results["comparison"]
            ComparisonSummary = ComparisonResults.get('summary', {})
            ComparisonParameters = ComparisonResults.get('parameters', {})
            ComparisonConfigName = Results.get('comparison_config_name', "Alternative Configuration")
            
            SummaryText += f"<h3>Comparison Configuration ({ComparisonConfigName})</h3>\n"
            
            # Create table for comparison parameters
            SummaryText += "<table border='1' cellpadding='4' cellspacing='0' style='border-collapse: collapse;'>\n"
            SummaryText += "<tr><th>Parameter</th><th>Original Value</th><th>Comparison Value</th></tr>\n"
            
            # Show all parameters used in the comparison benchmark
            for Param, Value in ComparisonParameters.items():
                OrigValue = Parameters.get(Param, Value)
                
                # Check if value is different from original benchmark
                IsDifferent = OrigValue != Value
                
                # Create row with highlighting if different
                if IsDifferent:
                    SummaryText += f"<tr><td>{Param}</td><td>{OrigValue}</td><td style='background-color: #FFFF99;'>{Value}</td></tr>\n"
                else:
                    SummaryText += f"<tr><td>{Param}</td><td>{OrigValue}</td><td>{Value}</td></tr>\n"
            
            SummaryText += "</table>\n"
            
            SummaryText += "<h3>Comparison Summary Statistics</h3>\n<ul>"
            SummaryText += f"<li><b>Total Tokens:</b> {ComparisonSummary.get('total_tokens', 0)}</li>"
            SummaryText += f"<li><b>Total Time:</b> {ComparisonSummary.get('total_time', 0):.2f} seconds</li>"
            SummaryText += f"<li><b>Average Tokens/Second:</b> {ComparisonSummary.get('average_tokens_per_second', 0):.2f}</li>"
            SummaryText += f"<li><b>Average Time/Test:</b> {ComparisonSummary.get('average_time_per_test', 0):.2f} seconds</li>"
            SummaryText += "</ul>\n"
            
            # Add performance comparison
            BaseTokensPerSecond = Summary.get('average_tokens_per_second', 0)
            CompTokensPerSecond = ComparisonSummary.get('average_tokens_per_second', 0)
            
            if BaseTokensPerSecond > 0 and CompTokensPerSecond > 0:
                Difference = ((CompTokensPerSecond - BaseTokensPerSecond) / BaseTokensPerSecond) * 100
                SummaryText += "<h3>Performance Comparison</h3>\n"
                if Difference > 0:
                    SummaryText += f"<p>The comparison configuration is <span style='color:green;'><b>{Difference:.2f}%</b> faster</span> than the base configuration.</p>\n"
                elif Difference < 0:
                    SummaryText += f"<p>The comparison configuration is <span style='color:red;'><b>{-Difference:.2f}%</b> slower</span> than the base configuration.</p>\n"
                else:
                    SummaryText += "<p>The comparison configuration has the same performance as the base configuration.</p>\n"
        
        # Update summary tab
        self.SummaryText.setHtml(SummaryText)
    
    def _CreateBenchmarkCharts(self, Results):
        """
        Create benchmark charts.
        
        Args:
            Results: Benchmark results
        """
        Tests = Results.get('tests', [])
        
        if not Tests:
            return
        
        # Clear charts tab
        self.ChartPlaceholder.setVisible(False)
        
        # Create a layout for the charts if it doesn't exist
        if not hasattr(self, 'ChartsLayout'):
            self.ChartsLayout = QVBoxLayout(self.ChartsTab)
        else:
            # Clear existing layout
            while self.ChartsLayout.count():
                Item = self.ChartsLayout.takeAt(0)
                if Item.widget():
                    Item.widget().deleteLater()
        
        # Create charts
        # This is a placeholder - in a real implementation, we would use a charting library
        # For now, we'll create a text-based chart
        ChartText = QTextEdit()
        ChartText.setReadOnly(True)
        
        ChartContent = "<h3>Tokens Per Second by Prompt</h3>\n"
        ChartContent += "<pre>\n"
        
        # Find max value for scaling
        MaxTokensPerSecond = max(test.get('tokens_per_second', 0) for test in Tests)
        ScaleFactor = 50 / (MaxTokensPerSecond if MaxTokensPerSecond > 0 else 1)
        
        for i, Test in enumerate(Tests):
            TokensPerSecond = Test.get('tokens_per_second', 0)
            BarLength = int(TokensPerSecond * ScaleFactor)
            Bar = "█" * BarLength
            
            ChartContent += f"Prompt {i+1}: {Bar} {TokensPerSecond:.2f} tokens/s\n"
        
        ChartContent += "</pre>\n"
        
        # Add comparison chart if available
        if "comparison" in Results:
            ComparisonResults = Results["comparison"]
            ComparisonTests = ComparisonResults.get('tests', [])
            
            if ComparisonTests:
                ChartContent += "<h3>Comparison: Tokens Per Second by Prompt</h3>\n"
                ChartContent += "<pre>\n"
                
                # Find max value for scaling
                CompMaxTokensPerSecond = max(test.get('tokens_per_second', 0) for test in ComparisonTests)
                MaxValue = max(MaxTokensPerSecond, CompMaxTokensPerSecond)
                CompScaleFactor = 50 / (MaxValue if MaxValue > 0 else 1)
                
                for i, Test in enumerate(ComparisonTests):
                    TokensPerSecond = Test.get('tokens_per_second', 0)
                    BarLength = int(TokensPerSecond * CompScaleFactor)
                    Bar = "█" * BarLength
                    
                    ChartContent += f"Prompt {i+1}: {Bar} {TokensPerSecond:.2f} tokens/s\n"
                
                ChartContent += "</pre>\n"
        
        ChartText.setHtml(ChartContent)
        self.ChartsLayout.addWidget(ChartText)
    
    def _DisplayBenchmarkDetails(self, Results):
        """
        Display detailed benchmark results.
        
        Args:
            Results: Benchmark results
        """
        Tests = Results.get('tests', [])
        
        if not Tests:
            return
        
        DetailsText = "<h3>Detailed Test Results</h3>\n"
        
        for i, Test in enumerate(Tests):
            DetailsText += f"<h4>Prompt {i+1}</h4>\n"
            DetailsText += f"<p><b>Prompt:</b> {Test.get('prompt', 'Unknown')}</p>\n"
            DetailsText += "<ul>\n"
            DetailsText += f"<li><b>Average Time:</b> {Test.get('average_time', 0):.2f} seconds</li>"
            DetailsText += f"<li><b>Average Tokens:</b> {Test.get('average_tokens', 0):.2f}</li>"
            DetailsText += f"<li><b>Average Output Tokens:</b> {Test.get('average_output_tokens', 0):.2f}</li>"
            DetailsText += f"<li><b>Tokens Per Second:</b> {Test.get('tokens_per_second', 0):.2f}</li>"
            DetailsText += f"<li><b>Successful Runs:</b> {Test.get('successful_runs', 0)}</li>"
            DetailsText += "</ul>\n"
        
        # Add comparison details if available
        if "comparison" in Results:
            ComparisonResults = Results["comparison"]
            ComparisonTests = ComparisonResults.get('tests', [])
            ComparisonConfigName = Results.get('comparison_config_name', "Alternative Configuration")
            
            if ComparisonTests:
                DetailsText += f"<h3>Comparison Detailed Results ({ComparisonConfigName})</h3>\n"
                
                for i, Test in enumerate(ComparisonTests):
                    DetailsText += f"<h4>Prompt {i+1}</h4>\n"
                    DetailsText += f"<p><b>Prompt:</b> {Test.get('prompt', 'Unknown')}</p>\n"
                    DetailsText += "<ul>\n"
                    DetailsText += f"<li><b>Average Time:</b> {Test.get('average_time', 0):.2f} seconds</li>"
                    DetailsText += f"<li><b>Average Tokens:</b> {Test.get('average_tokens', 0):.2f}</li>"
                    DetailsText += f"<li><b>Average Output Tokens:</b> {Test.get('average_output_tokens', 0):.2f}</li>"
                    DetailsText += f"<li><b>Tokens Per Second:</b> {Test.get('tokens_per_second', 0):.2f}</li>"
                    DetailsText += f"<li><b>Successful Runs:</b> {Test.get('successful_runs', 0)}</li>"
                    DetailsText += "</ul>\n"
        
        # Update details tab
        self.DetailsText.setHtml(DetailsText)
    
    def _OnSaveResults(self):
        """Handle save results button click."""
        if not self.CurrentResults:
            return
        
        # Get save file path
        FilePath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Benchmark Results",
            f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not FilePath:
            return
        
        try:
            # Save results to file
            with open(FilePath, 'w') as f:
                json.dump(self.CurrentResults, f, indent=2)
            
            # Show success message
            QMessageBox.information(
                self,
                "Save Successful",
                f"Benchmark results saved to {FilePath}"
            )
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Save Error",
                f"Error saving benchmark results: {e}"
            )