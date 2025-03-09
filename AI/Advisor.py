# File: Advisor.py
# Path: OllamaModelEditor/AI/Advisor.py
# Standard: AIDEV-PascalCase-1.0

import os
import logging
from typing import Dict, List, Any, Optional, Tuple

class ModelAdvisor:
    """Provides AI-powered advice for optimizing model parameters."""
    
    def __init__(self, config_manager, ollama_interface, logger=None):
        """Initialize the model advisor.
        
        Args:
            config_manager: The configuration manager instance
            ollama_interface: Interface for communicating with Ollama
            logger: Optional logger instance
        """
        self.Config = config_manager
        self.OllamaInterface = ollama_interface
        self.Logger = logger or logging.getLogger("ModelAdvisor")
        
        # Get advisor settings from config
        self.AdvisorSettings = self.Config.GetAIAdvisorSettings()
        self.AdvisorModel = self.AdvisorSettings.get("DefaultModel", "llama3")
        self.EnableAutoSuggestions = self.AdvisorSettings.get("EnableAutoSuggestions", True)
        self.ContextWindow = self.AdvisorSettings.get("ContextWindow", 4096)
    
    def GetAdvice(self, model_name: str, current_params: Dict[str, Any], 
                 use_case: str = None) -> Dict[str, Any]:
        """Get parameter advice for a specific model and use case.
        
        Args:
            model_name: Name of the target model
            current_params: Current parameter values
            use_case: Optional description of the intended use case
            
        Returns:
            Dict[str, Any]: Suggested parameter values and explanations
        """
        # In a real implementation, this would use the advisor model to generate advice
        # For now, we'll just provide some basic predefined advice
        
        self.Logger.info(f"Getting advice for {model_name} (use case: {use_case})")
        
        # Predefined advice for common use cases
        use_case_advice = {
            "creative": {
                "temperature": ("0.9", "Increased for more creative outputs"),
                "top_p": ("0.95", "Slightly increased for more variety"),
                "repeat_penalty": ("1.2", "Increased to reduce repetition in creative writing")
            },
            "factual": {
                "temperature": ("0.2", "Reduced for more deterministic, factual responses"),
                "top_p": ("0.6", "Reduced for more focused token selection"),
                "repeat_penalty": ("1.1", "Standard setting to avoid repetition")
            },
            "coding": {
                "temperature": ("0.2", "Low temperature for precise, deterministic code"),
                "top_p": ("0.7", "Moderately reduced for consistent code generation"),
                "repeat_penalty": ("1.05", "Slight penalty to avoid duplicate code")
            },
            "chat": {
                "temperature": ("0.7", "Balanced for conversational responses"),
                "top_p": ("0.9", "Standard setting for natural conversation"),
                "repeat_penalty": ("1.1", "Standard setting to avoid repetition")
            }
        }
        
        # Default advice if no use case specified
        if not use_case or use_case not in use_case_advice:
            use_case = "chat"  # Default to chat advice
        
        advice = use_case_advice[use_case]
        
        # Format the response
        result = {
            "model": model_name,
            "use_case": use_case,
            "suggested_parameters": {},
            "explanations": {}
        }
        
        for param, (value, explanation) in advice.items():
            result["suggested_parameters"][param] = value
            result["explanations"][param] = explanation
        
        self.Logger.info(f"Generated advice for {len(result['suggested_parameters'])} parameters")
        return result
    
    def AnalyzeParameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze parameter settings and identify potential issues or improvements.
        
        Args:
            parameters: Current parameter values
            
        Returns:
            Dict[str, Any]: Analysis results with warnings and suggestions
        """
        self.Logger.info("Analyzing parameters for potential issues")
        
        warnings = []
        suggestions = []
        
        # Check temperature
        temperature = float(parameters.get("temperature", 0.8))
        if temperature > 1.5:
            warnings.append("Temperature is very high, which may lead to incoherent outputs.")
            suggestions.append("Consider reducing temperature to between 0.7-1.0 for more balanced outputs.")
        elif temperature < 0.1:
            warnings.append("Temperature is very low, which may lead to repetitive or deterministic outputs.")
            suggestions.append("Consider increasing temperature slightly if more variety is desired.")
        
        # Check top_p and top_k interaction
        top_p = float(parameters.get("top_p", 0.9))
        top_k = int(parameters.get("top_k", 40))
        
        if top_p < 0.5 and top_k < 10:
            warnings.append("Both top_p and top_k are set to restrictive values, which may constrain the model too much.")
            suggestions.append("Consider increasing either top_p or top_k to allow more token diversity.")
        
        # Check context length
        num_ctx = int(parameters.get("num_ctx", 4096))
        if num_ctx > 16384:
            warnings.append("Very large context window may require significant memory resources.")
            suggestions.append("Ensure your system has adequate RAM for this context length.")
        
        # Check for conflicting sampling methods
        mirostat = int(parameters.get("mirostat", 0))
        if mirostat > 0 and (top_p < 1.0 or top_k < 100):
            warnings.append("Using Mirostat alongside restrictive top_p or top_k settings may lead to conflicts in sampling strategy.")
            suggestions.append("When using Mirostat, consider setting top_p=1.0 and top_k=100 (or higher) to let Mirostat control the sampling.")
        
        # Return analysis
        return {
            "warnings": warnings,
            "suggestions": suggestions,
            "parameter_count": len(parameters),
            "risk_level": "high" if len(warnings) > 2 else "medium" if len(warnings) > 0 else "low"
        }
    
    def SuggestParametersForUseCase(self, use_case: str) -> Dict[str, Any]:
        """Suggest parameter settings for a specific use case.
        
        Args:
            use_case: Description of the intended use case
            
        Returns:
            Dict[str, Any]: Suggested parameter values
        """
        self.Logger.info(f"Suggesting parameters for use case: {use_case}")
        
        # Predefined parameter sets for common use cases
        use_case_params = {
            "creative_writing": {
                "temperature": "0.9",
                "top_p": "0.95",
                "top_k": "60",
                "repeat_penalty": "1.2",
                "presence_penalty": "0.1",
                "frequency_penalty": "0.1"
            },
            "code_generation": {
                "temperature": "0.2",
                "top_p": "0.7",
                "top_k": "40",
                "repeat_penalty": "1.05",
                "presence_penalty": "0.0",
                "frequency_penalty": "0.0"
            },
            "factual_qa": {
                "temperature": "0.2",
                "top_p": "0.6",
                "top_k": "20",
                "repeat_penalty": "1.1",
                "presence_penalty": "0.0",
                "frequency_penalty": "0.0"
            },
            "summarization": {
                "temperature": "0.3",
                "top_p": "0.8",
                "top_k": "30",
                "repeat_penalty": "1.15",
                "presence_penalty": "0.0",
                "frequency_penalty": "0.2"
            },
            "chat_casual": {
                "temperature": "0.7",
                "top_p": "0.9",
                "top_k": "40",
                "repeat_penalty": "1.1",
                "presence_penalty": "0.0",
                "frequency_penalty": "0.0"
            },
            "roleplay": {
                "temperature": "0.8",
                "top_p": "0.95",
                "top_k": "60",
                "repeat_penalty": "1.15",
                "presence_penalty": "0.1",
                "frequency_penalty": "0.1"
            }
        }
        
        # Try to match the use case to our predefined sets
        matched_use_case = None
        for predefined_use_case in use_case_params.keys():
            if predefined_use_case.lower() in use_case.lower():
                matched_use_case = predefined_use_case
                break
        
        # If no match, use closest match based on keywords
        if not matched_use_case:
            keywords = {
                "creative_writing": ["creative", "write", "story", "poem", "novel"],
                "code_generation": ["code", "program", "function", "script", "algorithm"],
                "factual_qa": ["fact", "answer", "question", "accuracy", "information"],
                "summarization": ["summary", "summarize", "condense", "shorten"],
                "chat_casual": ["chat", "conversation", "talk", "discuss", "casual"],
                "roleplay": ["roleplay", "character", "pretend", "act", "simulate"]
            }
            
            # Count keyword matches for each use case
            matches = {}
            for uc, kws in keywords.items():
                matches[uc] = sum(1 for kw in kws if kw in use_case.lower())
            
            # Find the use case with most matches
            if any(matches.values()):
                matched_use_case = max(matches.items(), key=lambda x: x[1])[0]
            else:
                matched_use_case = "chat_casual"  # Default
        
        # Return the parameter set with metadata
        return {
            "use_case": use_case,
            "matched_category": matched_use_case,
            "parameters": use_case_params[matched_use_case],
            "description": f"Parameter set optimized for {matched_use_case.replace('_', ' ')}"
        }
