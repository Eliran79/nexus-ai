import os
from typing import Optional, Dict, Any

from .base import ModelInterface, ModelType, ExecutionMode, ModelUnavailableError
from .claude_local import ClaudeLocal
from .claude_api import ClaudeAPI
from .gemini_local import GeminiLocal


class ModelFactory:
    """Factory class for creating and managing AI model instances"""
    
    def __init__(self):
        self._instances: Dict[str, ModelInterface] = {}
        self._default_model = ModelType.CLAUDE  # Default to Claude
        self._default_mode = ExecutionMode.LOCAL  # Default to local execution
    
    def create_model(self, model_type: ModelType, execution_mode: ExecutionMode, **kwargs) -> ModelInterface:
        """Create a model instance
        
        Args:
            model_type: Type of model (CLAUDE, GEMINI)
            execution_mode: Execution mode (LOCAL, API)
            **kwargs: Additional arguments for model initialization
            
        Returns:
            Model instance
            
        Raises:
            ModelUnavailableError: If model cannot be created
            ValueError: If invalid combination requested
        """
        cache_key = f"{model_type.value}_{execution_mode.value}"
        
        # Return cached instance if available
        if cache_key in self._instances:
            return self._instances[cache_key]
        
        # Create new instance
        if model_type == ModelType.CLAUDE:
            if execution_mode == ExecutionMode.LOCAL:
                instance = ClaudeLocal()
            elif execution_mode == ExecutionMode.API:
                api_key = kwargs.get('api_key') or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ModelUnavailableError("ANTHROPIC_API_KEY not found for Claude API mode")
                instance = ClaudeAPI(api_key)
            else:
                raise ValueError(f"Invalid execution mode for Claude: {execution_mode}")
                
        elif model_type == ModelType.GEMINI:
            if execution_mode == ExecutionMode.LOCAL:
                instance = GeminiLocal()
            elif execution_mode == ExecutionMode.API:
                # TODO: Implement Gemini API when needed
                raise ModelUnavailableError("Gemini API mode not implemented yet")
            else:
                raise ValueError(f"Invalid execution mode for Gemini: {execution_mode}")
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Check if model is available
        if not instance.is_available():
            raise ModelUnavailableError(f"{instance.name} is not available")
        
        # Cache and return
        self._instances[cache_key] = instance
        return instance
    
    def get_model(self, model_name: str = None, execution_mode: ExecutionMode = None) -> ModelInterface:
        """Get a model instance by name and mode
        
        Args:
            model_name: Model name ('claude' or 'gemini'), uses default if None
            execution_mode: Execution mode, uses default if None
            
        Returns:
            Model instance
        """
        if model_name is None:
            model_type = self._default_model  # Always Claude by default
        else:
            try:
                model_type = ModelType(model_name.lower())
            except ValueError:
                raise ValueError(f"Unknown model: {model_name}")
        
        if execution_mode is None:
            execution_mode = self._default_mode  # Always local by default
        
        return self.create_model(model_type, execution_mode)
    
    def get_claude_local(self) -> ModelInterface:
        """Get Claude local instance"""
        return self.create_model(ModelType.CLAUDE, ExecutionMode.LOCAL)
    
    def get_claude_api(self, api_key: str = None) -> ModelInterface:
        """Get Claude API instance"""
        return self.create_model(ModelType.CLAUDE, ExecutionMode.API, api_key=api_key)
    
    def get_gemini_local(self) -> ModelInterface:
        """Get Gemini local instance"""
        return self.create_model(ModelType.GEMINI, ExecutionMode.LOCAL)
    
    def set_default_model(self, model_type: ModelType):
        """Set the default model type"""
        self._default_model = model_type
    
    def set_default_mode(self, execution_mode: ExecutionMode):
        """Set the default execution mode"""
        self._default_mode = execution_mode
    
    def get_available_models(self) -> Dict[str, Dict[str, bool]]:
        """Get availability status of all models
        
        Returns:
            Dict with model availability status
        """
        availability = {}
        
        for model_type in ModelType:
            availability[model_type.value] = {}
            
            for mode in ExecutionMode:
                try:
                    model = self.create_model(model_type, mode)
                    availability[model_type.value][mode.value] = model.is_available()
                except (ModelUnavailableError, ValueError):
                    availability[model_type.value][mode.value] = False
        
        return availability
    
    def clear_cache(self):
        """Clear all cached model instances"""
        self._instances.clear()


# Global factory instance
model_factory = ModelFactory()