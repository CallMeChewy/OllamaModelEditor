SummaryText += f"<li><b>Benchmark Date:</b> {Summary.get('benchmark_date', 'Unknown')}</li>"
        SummaryText += "</ul>\n"
        
        # Add comparison results if available
        if "comparison_tests" in Results:
            ComparisonSummary = Results.get('comparison_summary', {})
            ComparisonParameters = Results.get('comparison_config', {})
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
        if "comparison_tests" in Results:
            ComparisonTests = Results.get('comparison_tests', [])
            
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
                
                # Add side-by-side comparison chart
                ChartContent += "<h3>Side-by-Side Comparison</h3>\n"
                ChartContent += "<pre>\n"
                
                # Find min length of test arrays to compare
                CompLength = min(len(Tests), len(ComparisonTests))
                
                for i in range(CompLength):
                    BaseTest = Tests[i]
                    CompTest = ComparisonTests[i]
                    
                    BaseTokensPerSecond = BaseTest.get('tokens_per_second', 0)
                    CompTokensPerSecond = CompTest.get('tokens_per_second', 0)
                    
                    BaseBarLength = int(BaseTokensPerSecond * CompScaleFactor)
                    CompBarLength = int(CompTokensPerSecond * CompScaleFactor)
                    
                    BaseBar = "█" * BaseBarLength
                    CompBar = "█" * CompBarLength
                    
                    ChartContent += f"Prompt {i+1}:\n"
                    ChartContent += f"Base:    {BaseBar} {BaseTokensPerSecond:.2f} tokens/s\n"
                    ChartContent += f"Compare: {CompBar} {CompTokensPerSecond:.2f} tokens/s\n\n"
                
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
            DetailsText += f"<li><b>Average Input Tokens:</b> {Test.get('average_input_tokens', 0):.2f}</li>"
            DetailsText += f"<li><b>Average Output Tokens:</b> {Test.get('average_output_tokens', 0):.2f}</li>"
            DetailsText += f"<li><b>Tokens Per Second:</b> {Test.get('tokens_per_second', 0):.2f}</li>"
            DetailsText += f"<li><b>Successful Runs:</b> {Test.get('successful_runs', 0)}</li>"
            DetailsText += "</ul>\n"
        
        # Add comparison details if available
        if "comparison_tests" in Results:
            ComparisonTests = Results.get('comparison_tests', [])
            ComparisonConfigName = Results.get('comparison_config_name', "Alternative Configuration")
            
            if ComparisonTests:
                DetailsText += f"<h3>Comparison Detailed Results ({ComparisonConfigName})</h3>\n"
                
                for i, Test in enumerate(ComparisonTests):
                    DetailsText += f"<h4>Prompt {i+1}</h4>\n"
                    DetailsText += f"<p><b>Prompt:</b> {Test.get('prompt', 'Unknown')}</p>\n"
                    DetailsText += "<ul>\n"
                    DetailsText += f"<li><b>Average Time:</b> {Test.get('average_time', 0):.2f} seconds</li>"
                    DetailsText += f"<li><b>Average Input Tokens:</b> {Test.get('average_input_tokens', 0):.2f}</li>"
                    DetailsText += f"<li><b>Average Output Tokens:</b> {Test.get('average_output_tokens', 0):.2f}</li>"
                    DetailsText += f"<li><b>Tokens Per Second:</b> {Test.get('tokens_per_second', 0):.2f}</li>"
                    DetailsText += f"<li><b>Successful Runs:</b> {Test.get('successful_runs', 0)}</li>"
                    DetailsText += "</ul>\n"
                    
                    # Add direct comparison if possible
                    if i < len(Tests):
                        BaseTest = Tests[i]
                        
                        # Calculate performance difference
                        BaseTokensPerSecond = BaseTest.get('tokens_per_second', 0)
                        CompTokensPerSecond = Test.get('tokens_per_second', 0)
                        
                        if BaseTokensPerSecond > 0:
                            Difference = ((CompTokensPerSecond - BaseTokensPerSecond) / BaseTokensPerSecond) * 100
                            
                            if Difference > 0:
                                DetailsText += f"<p>This configuration is <span style='color:green;'><b>{Difference:.2f}%</b> faster</span> than the base configuration for this prompt.</p>\n"
                            elif Difference < 0:
                                DetailsText += f"<p>This configuration is <span style='color:red;'><b>{-Difference:.2f}%</b> slower</span> than the base configuration for this prompt.</p>\n"
                            else:
                                DetailsText += "<p>This configuration has the same performance as the base configuration for this prompt.</p>\n"
        
        # Update details tab
        self.DetailsText.setHtml(DetailsText)
    
    def _OnSaveResults(self):
        """Handle save results button click."""
        if not self.CurrentResults:
            return
        
        # Get save file path
        CurrentDatetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        DefaultFilename = f"benchmark_results_{CurrentDatetime}.json"
        
        FilePath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Benchmark Results",
            DefaultFilename,
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
