# Confirm with user
        Response = QMessageBox.question(
            self,
            "New Configuration",
            f"Create a new configuration for model {ModelName}?\n\nThis will reset all parameters to default values.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if Response == QMessageBox.Yes:
            # Reset parameters to default
            DefaultParams = self.Config.GetModelConfig('DefaultParameters')
            self.StateManager.UpdateCurrentState(ModelName, DefaultParams)
            
            # Update parameter editor
            self.ParameterEditorWidget.LoadModel(ModelName)
            
            self.StatusBar.showMessage(f"Created new configuration for {ModelName}", 3000)
    
    @Slot()
    def _OnOpenConfig(self) -> None:
        """Handle open configuration action."""
        # Get current model
        CurrentModel = self.ModelManager.GetCurrentModel()
        if not CurrentModel:
            QMessageBox.warning(
                self,
                "Open Configuration",
                "Please select a model first."
            )
            return
        
        ModelName = CurrentModel.get('name')
        
        # Get file path
        FilePath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Model Configuration",
            "",
            "JSON Files (*.json);;YAML Files (*.yaml *.yml);;All Files (*.*)"
        )
        
        if not FilePath:
            return
        
        # Import configuration
        Success = self.Config.ImportModelConfig(ModelName, FilePath)
        
        if Success:
            # Reload model in parameter editor
            self.ParameterEditorWidget.LoadModel(ModelName)
            
            self.StatusBar.showMessage(f"Configuration loaded for {ModelName}", 3000)
        else:
            QMessageBox.critical(
                self,
                "Open Configuration",
                f"Failed to load configuration from {FilePath}."
            )
    
    @Slot()
    def _OnSaveConfig(self) -> None:
        """Handle save configuration action."""
        # Get current model
        CurrentModel = self.ModelManager.GetCurrentModel()
        if not CurrentModel:
            QMessageBox.warning(
                self,
                "Save Configuration",
                "Please select a model first."
            )
            return
        
        ModelName = CurrentModel.get('name')
        
        # Commit current state
        if self.StateManager.CommitCurrentState(ModelName):
            self.StatusBar.showMessage(f"Configuration saved for {ModelName}", 3000)
        else:
            QMessageBox.critical(
                self,
                "Save Configuration",
                f"Failed to save configuration for {ModelName}."
            )
    
    @Slot()
    def _OnSaveConfigAs(self) -> None:
        """Handle save configuration as action."""
        # Get current model
        CurrentModel = self.ModelManager.GetCurrentModel()
        if not CurrentModel:
            QMessageBox.warning(
                self,
                "Save Configuration As",
                "Please select a model first."
            )
            return
        
        ModelName = CurrentModel.get('name')
        
        # Get save file path
        FilePath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Model Configuration",
            f"{ModelName}_config.json",
            "JSON Files (*.json);;YAML Files (*.yaml *.yml);;All Files (*.*)"
        )
        
        if not FilePath:
            return
        
        # Export configuration
        Success = self.Config.ExportModelConfig(ModelName, FilePath)
        
        if Success:
            self.StatusBar.showMessage(f"Configuration saved to {FilePath}", 3000)
        else:
            QMessageBox.critical(
                self,
                "Save Configuration As",
                f"Failed to save configuration to {FilePath}."
            )
    
    @Slot()
    def _OnPreferences(self) -> None:
        """Handle preferences action."""
        # TODO: Implement preferences dialog
        self.StatusBar.showMessage("Preferences not implemented yet", 3000)
    
    @Slot()
    def _OnBenchmark(self) -> None:
        """Handle benchmark action."""
        # Get current model
        CurrentModel = self.ModelManager.GetCurrentModel()
        if not CurrentModel:
            QMessageBox.warning(
                self,
                "Benchmark",
                "Please select a model first."
            )
            return
        
        # Switch to benchmark tab
        for i in range(self.TabWidget.count()):
            if self.TabWidget.tabText(i) == "Benchmark":
                self.TabWidget.setCurrentIndex(i)
                break
    
    @Slot()
    def _OnExportModel(self) -> None:
        """Handle export model definition action."""
        # Get current model
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
    
    @Slot()
    def _OnDocumentation(self) -> None:
        """Handle documentation action."""
        # TODO: Implement documentation viewer
        self.StatusBar.showMessage("Documentation not implemented yet", 3000)
    
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
