# File: ExportUtils.py
# Path: OllamaModelEditor/Utils/ExportUtils.py
# Standard: AIDEV-PascalCase-1.0

import os
import yaml
import json
import datetime
from typing import Dict, Any

class ExportManager:
    """Manages exporting and importing of model configurations."""
    
    def __init__(self, logger):
        """Initialize the export manager.
        
        Args:
            logger: Logger instance for logging
        """
        self.Logger = logger
    
    def ExportConfiguration(self, file_path: str, config_data: Dict[str, Any], model_name: str = None) -> bool:
        """Export a model configuration to a file.
        
        Args:
            file_path: Path to the export file
            config_data: Configuration data to export
            model_name: Optional model name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create export data with metadata
            ExportData = {
                "metadata": {
                    "created_at": datetime.datetime.now().isoformat(),
                    "model_name": model_name,
                    "format_version": "1.0"
                },
                "parameters": config_data
            }
            
            # Determine export format based on file extension
            _, Extension = os.path.splitext(file_path)
            
            if Extension.lower() == ".json":
                with open(file_path, "w") as f:
                    json.dump(ExportData, f, indent=2)
            else:
                # Default to YAML
                with open(file_path, "w") as f:
                    yaml.dump(ExportData, f, default_flow_style=False)
            
            self.Logger.info(f"Configuration exported to {file_path}")
            return True
            
        except Exception as e:
            self.Logger.error(f"Error exporting configuration: {e}")
            return False
    
    def ImportConfiguration(self, file_path: str) -> Dict[str, Any]:
        """Import a model configuration from a file.
        
        Args:
            file_path: Path to the import file
            
        Returns:
            Dict[str, Any]: The imported configuration data or empty dict on failure
        """
        try:
            # Determine import format based on file extension
            _, Extension = os.path.splitext(file_path)
            
            if Extension.lower() == ".json":
                with open(file_path, "r") as f:
                    ImportData = json.load(f)
            else:
                # Default to YAML
                with open(file_path, "r") as f:
                    ImportData = yaml.safe_load(f)
            
            # Extract parameters from the imported data
            if isinstance(ImportData, dict):
                if "parameters" in ImportData:
                    # New format with metadata
                    Parameters = ImportData["parameters"]
                else:
                    # Legacy format or direct parameters
                    Parameters = ImportData
            else:
                self.Logger.error(f"Invalid import data format in {file_path}")
                return {}
            
            self.Logger.info(f"Configuration imported from {file_path}")
            return Parameters
            
        except Exception as e:
            self.Logger.error(f"Error importing configuration: {e}")
            return {}
    
    def ExportModelComparison(self, file_path: str, comparison_data: Dict[str, Any]) -> bool:
        """Export a model comparison to a file.
        
        Args:
            file_path: Path to the export file
            comparison_data: Comparison data to export
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create export data with metadata
            ExportData = {
                "metadata": {
                    "created_at": datetime.datetime.now().isoformat(),
                    "type": "model_comparison",
                    "format_version": "1.0"
                },
                "comparison": comparison_data
            }
            
            # Determine export format based on file extension
            _, Extension = os.path.splitext(file_path)
            
            if Extension.lower() == ".json":
                with open(file_path, "w") as f:
                    json.dump(ExportData, f, indent=2)
            else:
                # Default to YAML
                with open(file_path, "w") as f:
                    yaml.dump(ExportData, f, default_flow_style=False)
            
            self.Logger.info(f"Comparison exported to {file_path}")
            return True
            
        except Exception as e:
            self.Logger.error(f"Error exporting comparison: {e}")
            return False