# File: Evaluation.py
# Path: OllamaModelEditor/AI/Evaluation.py
# Standard: AIDEV-PascalCase-1.0

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple

class ModelEvaluator:
    """Evaluates model performance with different parameter settings."""
    
    def __init__(self, config_manager, ollama_interface, logger=None):
        """Initialize the model evaluator.
        
        Args:
            config_manager: The configuration manager instance
            ollama_interface: Interface for communicating with Ollama
            logger: Optional logger instance
        """
        self.Config = config_manager
        self.OllamaInterface = ollama_interface
        self.Logger = logger or logging.getLogger("ModelEvaluator")
        self.EvaluationCache = {}
    
    def EvaluateParameterImpact(self, model_name: str, 
                                parameter_name: str,
                                test_values: List[Any],
                                base_parameters: Dict[str, Any] = None,
                                prompt: str = "Write a short story about a robot learning to feel emotions.") -> Dict[str, Any]:
        """Evaluate the impact of different values for a specific parameter.
        
        Args:
            model_name: Name of the model to evaluate
            parameter_name: Name of the parameter to test
            test_values: List of values to test for the parameter
            base_parameters: Base parameters to use for all tests
            prompt: Prompt to use for testing
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        self.Logger.info(f"Evaluating impact of parameter {parameter_name} on model {model_name}")
        
        base_params = base_parameters or {}
        results = []
        
        for value in test_values:
            # Create test parameters by updating the base parameters
            test_params = dict(base_params)
            test_params[parameter_name] = value
            
            # Run test with these parameters
            start_time = time.time()
            
            try:
                response = self.OllamaInterface.RunModel(model_name, prompt, test_params)
                
                # Calculate metrics
                elapsed_time = time.time() - start_time
                response_length = len(response.split())
                tokens_per_second = response_length / elapsed_time if elapsed_time > 0 else 0
                
                result = {
                    "parameter_value": value,
                    "elapsed_time": elapsed_time,
                    "response_length": response_length,
                    "tokens_per_second": tokens_per_second,
                    "success": True
                }
            except Exception as e:
                self.Logger.error(f"Error evaluating {parameter_name}={value}: {e}")
                result = {
                    "parameter_value": value,
                    "error": str(e),
                    "success": False
                }
            
            results.append(result)
            
            # Cache this result
            cache_key = f"{model_name}_{parameter_name}_{value}"
            self.EvaluationCache[cache_key] = result
            
            # Brief pause between tests to avoid rate limiting
            time.sleep(1)
        
        # Compile and return results
        evaluation = {
            "model": model_name,
            "parameter": parameter_name,
            "test_values": test_values,
            "base_parameters": base_parameters,
            "results": results,
            "timestamp": time.time()
        }
        
        return evaluation
    
    def IdentifyOptimalValue(self, evaluation_results: Dict[str, Any]) -> Tuple[Any, str]:
        """Identify the optimal value from evaluation results.
        
        Args:
            evaluation_results: Results from EvaluateParameterImpact
            
        Returns:
            Tuple[Any, str]: Optimal value and reason
        """
        if not evaluation_results or "results" not in evaluation_results:
            return (None, "No evaluation results available")
        
        # Filter successful results
        successful_results = [r for r in evaluation_results["results"] if r.get("success", False)]
        
        if not successful_results:
            return (None, "No successful evaluations")
        
        # Find the value with highest tokens per second
        fastest = max(successful_results, key=lambda r: r.get("tokens_per_second", 0))
        
        # Find the value with longest response
        longest = max(successful_results, key=lambda r: r.get("response_length", 0))
        
        # Use the fastest unless it's much shorter
        if fastest.get("response_length", 0) < longest.get("response_length", 0) * 0.7:
            # If the fastest response is less than 70% of the longest, prefer the middle ground
            # Sort by a combined metric of speed and length
            combined = sorted(successful_results, 
                            key=lambda r: (r.get("tokens_per_second", 0) * 0.7 + 
                                        r.get("response_length", 0) / longest.get("response_length", 1) * 0.3),
                            reverse=True)
            optimal = combined[0]
            reason = "Balanced speed and response quality"
        else:
            optimal = fastest
            reason = "Fastest response without significant quality loss"
        
        return (optimal.get("parameter_value"), reason)
    
    def RunParameterSensitivityAnalysis(self, model_name: str, 
                                       parameters_to_test: Dict[str, List[Any]],
                                       base_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run sensitivity analysis for multiple parameters.
        
        Args:
            model_name: Name of the model
            parameters_to_test: Dictionary mapping parameter names to lists of test values
            base_parameters: Base parameters to use
            
        Returns:
            Dict[str, Any]: Sensitivity analysis results
        """
        self.Logger.info(f"Running parameter sensitivity analysis for model {model_name}")
        
        results = {}
        optimal_values = {}
        
        for param_name, test_values in parameters_to_test.items():
            self.Logger.info(f"Testing parameter: {param_name}")
            
            # Run evaluation for this parameter
            evaluation = self.EvaluateParameterImpact(
                model_name,
                param_name,
                test_values,
                base_parameters
            )
            
            results[param_name] = evaluation
            
            # Identify optimal value
            optimal_value, reason = self.IdentifyOptimalValue(evaluation)
            optimal_values[param_name] = {
                "value": optimal_value,
                "reason": reason
            }
        
        # Return complete analysis
        return {
            "model": model_name,
            "base_parameters": base_parameters,
            "parameter_evaluations": results,
            "optimal_values": optimal_values,
            "timestamp": time.time()
        }
    
    def SaveEvaluationResults(self, results: Dict[str, Any], file_path: str) -> bool:
        """Save evaluation results to a file.
        
        Args:
            results: Evaluation results to save
            file_path: Path to save results
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
                
            self.Logger.info(f"Evaluation results saved to {file_path}")
            return True
            
        except Exception as e:
            self.Logger.error(f"Error saving evaluation results: {e}")
            return False
    
    def LoadEvaluationResults(self, file_path: str) -> Dict[str, Any]:
        """Load evaluation results from a file.
        
        Args:
            file_path: Path to load results from
            
        Returns:
            Dict[str, Any]: Loaded evaluation results or empty dict on error
        """
        try:
            with open(file_path, 'r') as f:
                results = json.load(f)
                
            self.Logger.info(f"Evaluation results loaded from {file_path}")
            return results
            
        except Exception as e:
            self.Logger.error(f"Error loading evaluation results: {e}")
            return {}