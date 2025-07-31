import asyncio
import subprocess
import shutil
from typing import Optional

from .base import ModelInterface, ModelType, ExecutionMode, ModelUnavailableError, ModelExecutionError


class ClaudeLocal(ModelInterface):
    """Local Claude implementation using system claude command"""
    
    def __init__(self):
        super().__init__(ModelType.CLAUDE, ExecutionMode.LOCAL)
    
    def is_available(self) -> bool:
        """Check if claude command is available in system PATH"""
        if self._available is None:
            self._available = shutil.which("claude") is not None
        return self._available
    
    async def get_response(self, message: str, context: str = "") -> str:
        """Get response from local Claude using claude -p command
        
        Args:
            message: User message/query
            context: Additional context from session history
            
        Returns:
            Claude's response as string
            
        Raises:
            ModelUnavailableError: If claude command not found
            ModelExecutionError: If claude execution fails
        """
        if not self.is_available():
            raise ModelUnavailableError("Claude command not found in system PATH")
        
        # Prepare the full prompt with context
        full_prompt = self._prepare_prompt(message, context)
        
        try:
            # Execute claude -p with the prompt via stdin (handles multiline properly)
            process = await asyncio.create_subprocess_exec(
                "claude", "-p",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Encode the input as bytes
            input_bytes = full_prompt.encode('utf-8')
            
            # Add timeout to prevent hanging
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(input=input_bytes), 
                    timeout=60
                )
            except asyncio.TimeoutError:
                # Kill the process if it times out
                process.kill()
                await process.wait()
                raise ModelExecutionError("Claude command timed out after 60 seconds")
            
            # Decode the output
            stdout = stdout_bytes.decode('utf-8') if stdout_bytes else ''
            stderr = stderr_bytes.decode('utf-8') if stderr_bytes else ''
            
            if process.returncode != 0:
                error_msg = stderr.strip() if stderr else f"Claude command failed with code {process.returncode}"
                raise ModelExecutionError(f"Claude execution failed: {error_msg}")
            
            return stdout.strip()
            
        except FileNotFoundError:
            raise ModelUnavailableError("Claude command not found")
        except Exception as e:
            raise ModelExecutionError(f"Error executing Claude: {str(e)}")
    
    def _prepare_prompt(self, message: str, context: str = "") -> str:
        """Prepare the full prompt with context for Claude
        
        Args:
            message: User message
            context: Session context
            
        Returns:
            Formatted prompt string
        """
        if context.strip():
            return f"""Previous context:
{context}

Current query:
{message}"""
        else:
            return message
    
    def get_response_sync(self, message: str, context: str = "") -> str:
        """Synchronous version of get_response for backward compatibility
        
        Args:
            message: User message/query
            context: Additional context from session history
            
        Returns:
            Claude's response as string
        """
        if not self.is_available():
            raise ModelUnavailableError("Claude command not found in system PATH")
        
        full_prompt = self._prepare_prompt(message, context)
        
        try:
            result = subprocess.run(
                ["claude", "-p"],
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else f"Claude command failed with code {result.returncode}"
                raise ModelExecutionError(f"Claude execution failed: {error_msg}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise ModelExecutionError("Claude command timed out")
        except FileNotFoundError:
            raise ModelUnavailableError("Claude command not found")
        except Exception as e:
            raise ModelExecutionError(f"Error executing Claude: {str(e)}")