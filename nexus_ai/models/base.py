from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum


class ModelType(Enum):
    """Supported model types"""
    CLAUDE = "claude"
    GEMINI = "gemini"


class ExecutionMode(Enum):
    """Model execution modes"""
    LOCAL = "local"
    API = "api"


class ModelInterface(ABC):
    """Base interface for all AI model implementations"""
    
    def __init__(self, model_type: ModelType, execution_mode: ExecutionMode):
        self.model_type = model_type
        self.execution_mode = execution_mode
        self._available = None
    
    @abstractmethod
    async def get_response(self, message: str, context: str = "") -> str:
        """Get response from the model
        
        Args:
            message: User message/query
            context: Additional context from session history
            
        Returns:
            Model response as string
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model backend is available
        
        Returns:
            True if model can be used, False otherwise
        """
        pass
    
    @property
    def name(self) -> str:
        """Get human-readable model name"""
        return f"{self.model_type.value}-{self.execution_mode.value}"
    
    def __str__(self) -> str:
        return self.name


class ModelError(Exception):
    """Base exception for model-related errors"""
    pass


class ModelUnavailableError(ModelError):
    """Raised when a model backend is not available"""
    pass


class ModelExecutionError(ModelError):
    """Raised when model execution fails"""
    pass