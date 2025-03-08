# File: OllamaUtils.py
# Path: OllamaModelEditor/Utils/OllamaUtils.py
# Standard: AIDEV-PascalCase-1.0

import subprocess
import os
import re
import tempfile
import logging
from typing import Dict, List, Any, Optional, Tuple

class OllamaInterface:
    """Interface for interacting with the Ollama CLI."""
    
    def __init__(self, logger=None):
        """Initialize the Ollama interface.
        
        Args:
            logger: Optional logger instance
        """
        self.Logger = logger or logging.getLogger("OllamaModelEditor")
        self.TempDir = os.path.join(os.path.expanduser("~"), ".ollama_editor", "temp")
        os.makedirs(self.TempDir, exist_ok=True)
    
    def _RunCommand(self, cmd_args: List[str], check=True) -> Tuple[bool, str, str]:
        """Run an Ollama command.
        
        Args:
            cmd_args: List of command arguments
            check: Whether to check for errors
            
        Returns:
            Tuple[bool, str, str]: (Success, stdout, stderr)
        """
        try:
            self.Logger.debug(f"Running command: ollama {' '.join(cmd_args)}")
            
            Result = subprocess.run(
                ["ollama"] + cmd_args,
                capture_output=True,
                text=True,
                check=check
            )
            
            if Result.returncode == 0:
                return True, Result.stdout, Result.stderr
            else:
                self.Logger.error(f"Command failed: {Result.stderr}")
                return False, Result.stdout, Result.stderr
                
        except subprocess.CalledProcessError as e:
            self.Logger.error(f"Command error: {e}")
            return False, e.stdout if hasattr(e, 'stdout') else "", e.stderr if hasattr(e, 'stderr') else str(e)
        except Exception as e:
            self.Logger.error(f"Unexpected error: {e}")
            return False, "", str(e)
    
    def ListModels(self) -> List[str]:
        """List all available Ollama models.
        
        Returns:
            List[str]: List of model names
        """
        Success, Stdout, Stderr = self._RunCommand(["list"])
        
        if not Success:
            self.Logger.error(f"Failed to list models: {Stderr}")
            return []
        
        # Parse model names from output
        Models = []
        
        # Skip header line
        Lines = Stdout.strip().split("\n")[1:]
        
        for Line in Lines:
            if Line.strip():
                # Extract model name (first column)
                ModelName = Line.split()[0]
                if ":" in ModelName:
                    ModelName = ModelName.split(":")[0]  # Remove tag if present
                Models.append(ModelName)
        
        # Remove duplicates and sort
        return sorted(list(set(Models)))
    
    def ShowModel(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict[str, Any]: Dictionary with model details
        """
        Success, Stdout, Stderr = self._RunCommand(["show", model_name])
        
        if not Success:
            self.Logger.error(f"Failed to show model {model_name}: {Stderr}")
            return {}
        
        # Parse model details
        Details = {
            "architecture": "",
            "parameters": "",
            "context_length": "",
            "embedding_length": "",
            "quantization": "",
            "license": ""
        }
        
        # Extract info using regex patterns
        ArchitectureMatch = re.search(r"architecture\s+(\S+)", Stdout)
        if ArchitectureMatch:
            Details["architecture"] = ArchitectureMatch.group(1)
            
        ParametersMatch = re.search(r"parameters\s+(\S+)", Stdout)
        if ParametersMatch:
            Details["parameters"] = ParametersMatch.group(1)
            
        ContextMatch = re.search(r"context length\s+(\S+)", Stdout)
        if ContextMatch:
            Details["context_length"] = ContextMatch.group(1)
            
        EmbeddingMatch = re.search(r"embedding length\s+(\S+)", Stdout)
        if EmbeddingMatch:
            Details["embedding_length"] = EmbeddingMatch.group(1)
            
        QuantizationMatch = re.search(r"quantization\s+(\S+)", Stdout)
        if QuantizationMatch:
            Details["quantization"] = QuantizationMatch.group(1)
        
        # Look for license information
        LicenseLines = []
        InLicenseSection = False
        for Line in Stdout.split("\n"):
            if Line.strip() == "License":
                InLicenseSection = True
                continue
            if InLicenseSection and Line.strip():
                LicenseLines.append(Line.strip())
        
        if LicenseLines:
            Details["license"] = LicenseLines[0]
        
        return Details
    
    def ShowModelfile(self, model_name: str) -> str:
        """Get the modelfile for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            str: Modelfile content
        """
        Success, Stdout, Stderr = self._RunCommand(["show", "--modelfile", model_name])
        
        if not Success:
            self.Logger.error(f"Failed to get modelfile for {model_name}: {Stderr}")
            return ""
        
        return Stdout
    
    def CreateModel(self, model_name: str, modelfile_content: str) -> bool:
        """Create a new model.
        
        Args:
            model_name: Name for the new model
            modelfile_content: Content of the modelfile
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Create a temporary Modelfile
        ModelfilePath = os.path.join(self.TempDir, "Modelfile")
        
        try:
            with open(ModelfilePath, "w") as f:
                f.write(modelfile_content)
            
            Success, Stdout, Stderr = self._RunCommand(
                ["create", model_name, "-f", ModelfilePath],
                check=False  # Don't raise exception, we'll handle errors
            )
            
            if not Success:
                self.Logger.error(f"Failed to create model {model_name}: {Stderr}")
                return False
            
            return True
            
        except Exception as e:
            self.Logger.error(f"Error creating model: {e}")
            return False
    
    def RunModel(self, model_name: str, prompt: str, params: Dict[str, Any] = None) -> str:
        """Run a model with a prompt.
        
        Args:
            model_name: Name of the model
            prompt: Prompt to send to the model
            params: Optional parameters to use
            
        Returns:
            str: Model response
        """
        Cmd = ["run", model_name]
        
        # Add parameters if provided
        if params:
            for Key, Value in params.items():
                Cmd.extend([f"--{Key}", str(Value)])
        
        # Create a temporary file for the prompt
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(prompt)
            PromptFile = f.name
        
        try:
            # Use the prompt file as input
            with open(PromptFile, 'r') as f:
                Success, Stdout, Stderr = self._RunCommand(Cmd, check=False, stdin=f)
            
            if not Success:
                self.Logger.error(f"Failed to run model {model_name}: {Stderr}")
                return Stderr
            
            return Stdout
            
        except Exception as e:
            self.Logger.error(f"Error running model: {e}")
            return f"Error: {str(e)}"
        finally:
            # Clean up the temporary file
            if os.path.exists(PromptFile):
                os.remove(PromptFile)
    
    def DeleteModel(self, model_name: str) -> bool:
        """Delete a model.
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        Success, Stdout, Stderr = self._RunCommand(["rm", model_name], check=False)
        
        if not Success:
            self.Logger.error(f"Failed to delete model {model_name}: {Stderr}")
            return False
        
        return True
    
    def GetModelVersions(self, model_name: str) -> List[str]:
        """Get available versions of a model.
        
        Args:
            model_name: Base model name
            
        Returns:
            List[str]: List of model versions
        """
        Success, Stdout, Stderr = self._RunCommand(["list"])
        
        if not Success:
            self.Logger.error(f"Failed to list models: {Stderr}")
            return []
        
        Versions = []
        
        # Skip header line
        Lines = Stdout.strip().split("\n")[1:]
        
        for Line in Lines:
            if Line.strip():
                # Extract model name with tag
                FullName = Line.split()[0]
                if FullName.startswith(f"{model_name}:"):
                    Versions.append(FullName)
        
        return Versions