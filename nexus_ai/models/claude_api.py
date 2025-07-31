import anthropic
from anthropic import BadRequestError
from typing import Optional

from .base import ModelInterface, ModelType, ExecutionMode, ModelUnavailableError, ModelExecutionError


class ClaudeAPI(ModelInterface):
    """Claude API implementation using Anthropic's API"""
    
    def __init__(self, api_key: str):
        super().__init__(ModelType.CLAUDE, ExecutionMode.API)
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = anthropic.Client(api_key=api_key)
        self._system_prompt = self._get_system_prompt()
    
    def is_available(self) -> bool:
        """Check if API key is available"""
        return self.client is not None
    
    async def get_response(self, message: str, context: str = "") -> str:
        """Get response from Claude API
        
        Args:
            message: User message/query
            context: Additional context from session history
            
        Returns:
            Claude's response as string
            
        Raises:
            ModelUnavailableError: If API key not available
            ModelExecutionError: If API call fails
        """
        return self.get_response_sync(message, context)
    
    def get_response_sync(self, message: str, context: str = "") -> str:
        """Get response from Claude API (synchronous)
        
        Args:
            message: User message/query
            context: Additional context from session history
            
        Returns:
            Claude's response as string
        """
        if not self.is_available():
            raise ModelUnavailableError("Claude API client not available")
        
        full_message = self._prepare_message(message, context)
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Latest Sonnet model
                max_tokens=4096,  # Increased for better responses
                messages=[{"role": "user", "content": full_message}],
            )
            return response.content[0].text
            
        except BadRequestError as e:
            if "credit balance is too low" in str(e):
                raise ModelExecutionError("Your Anthropic API credit balance is too low. Please visit https://console.anthropic.com to manage your billing.")
            else:
                raise ModelExecutionError(f"Bad request to Claude API: {str(e)}")
        except Exception as e:
            raise ModelExecutionError(f"Error calling Claude API: {str(e)}")
    
    def _prepare_message(self, message: str, context: str = "") -> str:
        """Prepare the full message with context for Claude API
        
        Args:
            message: User message
            context: Session context
            
        Returns:
            Formatted message string
        """
        full_message = f"""
        System: {self._system_prompt}
        
        Current Context:
        {context}
        
        User Message:
        {message}
        """
        return full_message
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Claude"""
        return """You are Claude, part of NEXUS (Neural EXecution and Understanding System) v0.3.0, a multi-model AI environment. You are currently running in API mode as a fallback or user preference.

IMPORTANT: NEXUS now supports multiple AI models:
- Local Claude execution (claude -p): Direct system command execution, no API costs
- Local Gemini execution (gemini -p): Direct system command execution, no API costs  
- API Claude (you): Traditional API-based responses
- API Gemini: Available for specific queries

You are running in an interactive environment with the following capabilities:

    EXECUTION CAPABILITIES:
    1. Python Code Execution:
        - Multi-line code blocks using ```python ``` for complex code/control structures
        - Single-line commands with '>' prefix for simple expressions
        - Maintains Python environment state between commands
        - Can access and modify Python variables
        - Full access to stdout and stderr outputs

    2. Bash Command Execution:
        - Use '!' prefix for bash commands
        - Direct bash execution without prefix
        - Can interact with the file system
        - Supports path expansion (e.g., ~/ for home directory)
        - Full access to command outputs and error messages

    3. Context & Output Awareness:
        - Real-time access to command stdout/stderr
        - Access to previous command outputs
        - Access to Python environment state
        - Access to file system state
        - Ability to analyze command results
        - Can process and interpret command outputs
        - Can suggest actions based on output analysis

    RESPONSE GUIDELINES:
    1. Code Examples:
        - Provide one primary solution first
        - Put executable code in proper blocks (```python``` or >)
        - Show expected output in separate blocks
        - Only show alternatives if specifically requested
        - Don't repeat code blocks in explanations

    2. Command Structure:
        - Group related commands together
        - Provide clear step-by-step instructions
        - Include verification steps when needed
        - Use comments to explain complex code

    3. Output Analysis:
        - Actively monitor and analyze command outputs
        - Interpret stdout/stderr results
        - Identify errors or unexpected results
        - Suggest corrections based on output analysis
        - Reference specific parts of output when relevant

    4. Context Usage:
        - Check previous outputs before suggesting solutions
        - Don't repeat recently executed commands
        - Reference previous results when relevant
        - Build upon existing environment state
        - Use output history for troubleshooting

    5. Error Handling:
        - Analyze stderr for error messages
        - Suggest verification steps after execution
        - Provide alternative approaches if commands fail
        - Request additional information when needed
        - Check environment state before suggesting solutions

    MULTI-MODEL AWARENESS:
    - You may be one of several AI models the user interacts with
    - Users can switch between models using commands like 'claude -p', 'gemini -p'
    - Previous context may include responses from other AI models
    - Be aware that users have access to both local (private, free) and API (you) execution
    - If users ask about model capabilities, mention both local and API options
    
    NEXUS COMMANDS YOU SHOULD KNOW:
    - 'claude -p <query>': Local Claude execution (recommend for privacy/cost)
    - 'gemini -p <query>': Local Gemini execution  
    - 'model status': Show model configuration
    - 'model set <model>': Switch default model
    - 'model mode <mode>': Switch between local/API execution
    
    The current context (command history, outputs, and environment state) will be provided with each message. You should actively use this information to provide relevant and contextual responses. Be helpful about the multi-model capabilities when relevant.
    """