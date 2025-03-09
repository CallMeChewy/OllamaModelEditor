# File: BenchmarkingUtils.py
# Path: OllamaModelEditor/Utils/BenchmarkingUtils.py
# Standard: AIDEV-PascalCase-1.0

import time
import json
import os
import datetime
import statistics
import threading
import re
from typing import Dict, List, Any, Optional, Tuple

class BenchmarkRunner:
    """Runs benchmarks for Ollama models."""
    
    def __init__(self, ollama_interface, logger):
        """Initialize the benchmark runner.
        
        Args:
            ollama_interface: Interface for communicating with Ollama
            logger: Logger instance for logging
        """
        self.OllamaInterface = ollama_interface
        self.Logger = logger
        self.DefaultPrompts = self._LoadDefaultPrompts()
        self.Results = {}
        self.StopBenchmark = False
    
    def _LoadDefaultPrompts(self) -> Dict[str, str]:
        """Load default benchmark prompts.
        
        Returns:
            Dict[str, str]: Dictionary of benchmark prompts
        """
        return {
            "basic": "Hello, how are you today?",
            "creative": "Write a short poem about artificial intelligence.",
            "factual": "Explain how a transformer neural network works.",
            "instruction": "Sort the following list in descending order: 5, 2, 9, 1, 7, 3.",
            "code": "Write a Python function to calculate the factorial of a number.",
            "long_context": "Summarize the following text: " + (" This is a sample text. " * 50)
        }
    
    def RunSingleBenchmark(self, model_name: str, prompt_type: str = "basic", 
                          parameters: Dict[str, Any] = None, 
                          custom_prompt: str = None) -> Dict[str, Any]:
        """Run a single benchmark test.
        
        Args:
            model_name: Name of the model to benchmark
            prompt_type: Type of prompt to use (from default prompts)
            parameters: Optional parameters to use
            custom_prompt: Optional custom prompt text (overrides prompt_type)
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        self.Logger.info(f"Running benchmark for model {model_name}")
        
        # Select prompt
        Prompt = custom_prompt if custom_prompt else self.DefaultPrompts.get(prompt_type, self.DefaultPrompts["basic"])
        
        Start = time.time()
        
        try:
            # Run the model
            Response = self.OllamaInterface.RunModel(model_name, Prompt, parameters)
            
            # Calculate metrics
            End = time.time()
            ElapsedTime = End - Start
            
            # Count tokens in response (approximation)
            TokenCount = len(Response.split())
            TokensPerSecond = TokenCount / ElapsedTime if ElapsedTime > 0 else 0
            
            self.Logger.info(f"Benchmark complete: {TokensPerSecond:.2f} tokens/sec")
            
            # Return results
            return {
                "model": model_name,
                "prompt_type": prompt_type if not custom_prompt else "custom",
                "parameters": parameters or {},
                "elapsed_time": ElapsedTime,
                "token_count": TokenCount,
                "tokens_per_second": TokensPerSecond,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            self.Logger.error(f"Benchmark error: {e}")
            
            # Return error results
            return {
                "model": model_name,
                "prompt_type": prompt_type if not custom_prompt else "custom",
                "parameters": parameters or {},
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def StopRunningBenchmarks(self):
        """Stop all running benchmarks."""
        self.StopBenchmark = True
        self.Logger.info("Stopping benchmarks...")
    
    def RunComparativeBenchmark(self, model_configs: List[Dict[str, Any]], 
                               prompt_type: str = "basic",
                               custom_prompt: str = None,
                               runs_per_config: int = 3,
                               callback = None) -> Dict[str, Any]:
        """Run comparative benchmarks across multiple model configurations.
        
        Args:
            model_configs: List of model configurations to benchmark
                           Each config should have "model" and "parameters" keys
            prompt_type: Type of prompt to use
            custom_prompt: Optional custom prompt text
            runs_per_config: Number of benchmark runs per configuration
            callback: Optional callback function to update progress
            
        Returns:
            Dict[str, Any]: Comparative benchmark results
        """
        self.Logger.info(f"Starting comparative benchmark with {len(model_configs)} configurations")
        self.StopBenchmark = False
        Results = {}
        
        for i, Config in enumerate(model_configs):
            if self.StopBenchmark:
                self.Logger.info("Benchmark stopped by user")
                break
                
            ModelName = Config.get("model", "")
            Parameters = Config.get("parameters", {})
            ConfigName = Config.get("name", f"Config {i+1}")
            
            if not ModelName:
                self.Logger.error(f"Skipping config with no model name: {ConfigName}")
                continue
            
            self.Logger.info(f"Benchmarking {ConfigName} ({ModelName}) - Run 1/{runs_per_config}")
            
            # Run multiple benchmarks for this configuration
            ConfigResults = []
            for run in range(runs_per_config):
                if self.StopBenchmark:
                    break
                    
                if callback:
                    callback(i, len(model_configs), run, runs_per_config, ConfigName)
                    
                RunResult = self.RunSingleBenchmark(
                    ModelName, 
                    prompt_type, 
                    Parameters,
                    custom_prompt
                )
                
                ConfigResults.append(RunResult)
                
                # Sleep briefly between runs
                if run < runs_per_config - 1:
                    time.sleep(1)
            
            # Calculate aggregated metrics
            if ConfigResults and "error" not in ConfigResults[0]:
                TimesArray = [r["elapsed_time"] for r in ConfigResults if "elapsed_time" in r]
                TokensArray = [r["tokens_per_second"] for r in ConfigResults if "tokens_per_second" in r]
                
                if TimesArray and TokensArray:
                    Results[ConfigName] = {
                        "model": ModelName,
                        "parameters": Parameters,
                        "runs": len(ConfigResults),
                        "avg_elapsed_time": statistics.mean(TimesArray),
                        "min_elapsed_time": min(TimesArray),
                        "max_elapsed_time": max(TimesArray),
                        "avg_tokens_per_second": statistics.mean(TokensArray),
                        "min_tokens_per_second": min(TokensArray),
                        "max_tokens_per_second": max(TokensArray),
                        "individual_results": ConfigResults
                    }
            else:
                # Handle error case
                Results[ConfigName] = {
                    "model": ModelName,
                    "parameters": Parameters,
                    "error": ConfigResults[0].get("error", "Unknown error"),
                    "individual_results": ConfigResults
                }
        
        # Store overall results
        self.Results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "prompt_type": prompt_type if not custom_prompt else "custom",
            "runs_per_config": runs_per_config,
            "configurations": Results
        }
        
        self.Logger.info("Comparative benchmark complete")
        return self.Results
    
    def SaveBenchmarkResults(self, file_path: str) -> bool:
        """Save benchmark results to a file.
        
        Args:
            file_path: Path to save the results
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.Results:
            self.Logger.error("No benchmark results to save")
            return False
        
        try:
            # Ensure directory exists
            Directory = os.path.dirname(file_path)
            if Directory and not os.path.exists(Directory):
                os.makedirs(Directory)
            
            # Save results
            with open(file_path, 'w') as f:
                json.dump(self.Results, f, indent=2)
                
            self.Logger.info(f"Benchmark results saved to {file_path}")
            return True
            
        except Exception as e:
            self.Logger.error(f"Error saving benchmark results: {e}")
            return False
    
    def LoadBenchmarkResults(self, file_path: str) -> bool:
        """Load benchmark results from a file.
        
        Args:
            file_path: Path to load the results from
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                self.Results = json.load(f)
                
            self.Logger.info(f"Benchmark results loaded from {file_path}")
            return True
            
        except Exception as e:
            self.Logger.error(f"Error loading benchmark results: {e}")
            return False
    
    def GetResults(self) -> Dict[str, Any]:
        """Get the current benchmark results.
        
        Returns:
            Dict[str, Any]: Benchmark results
        """
        return self.Results