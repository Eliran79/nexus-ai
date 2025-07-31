"""
NEXUS AI Models Package

This package provides abstractions and implementations for different AI models
supporting both local execution and API-based execution modes.
"""

from .base import ModelInterface, ModelType, ExecutionMode, ModelError, ModelUnavailableError, ModelExecutionError
from .claude_local import ClaudeLocal
from .claude_api import ClaudeAPI
from .gemini_local import GeminiLocal
from .factory import ModelFactory, model_factory

__all__ = [
    # Base classes and enums
    'ModelInterface',
    'ModelType', 
    'ExecutionMode',
    'ModelError',
    'ModelUnavailableError',
    'ModelExecutionError',
    
    # Model implementations
    'ClaudeLocal',
    'ClaudeAPI', 
    'GeminiLocal',
    
    # Factory
    'ModelFactory',
    'model_factory',
]