# nexus_ai/repl/prompt_toolkit_repl.py
import asyncio
import sys
import os
from typing import Optional, List, Dict, Any
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import HTML
from pygments.lexers import PythonLexer, BashLexer

from nexus_ai.core.session import Session
from nexus_ai.core.executor import CodeExecutor
from nexus_ai.claude.client import ClaudeClient
from nexus_ai.models import model_factory, ModelType, ExecutionMode, ModelUnavailableError, ModelExecutionError
from anthropic import BadRequestError


class NexusCompleter(Completer):
    """Custom completer for NEXUS commands"""
    
    def __init__(self):
        self.nexus_commands = [
            '> ',  # Python
            '!',   # Bash
            '!i ', # Interactive bash
            '!c ', # Captured bash
            '??',  # Claude query
            'claude ',  # Claude API query (backward compatibility)
            'claude -p ',  # Claude local query
            'gemini ',  # Gemini API query
            'gemini -p ',  # Gemini local query
            'model ',   # Model commands
            'task:',    # Task
            'exit',     # Exit
            'quit',     # Quit
            'help',     # Help
        ]
        
        # Common Python keywords for completion
        self.python_keywords = [
            'print', 'import', 'def', 'class', 'if', 'else', 'elif', 'for', 
            'while', 'try', 'except', 'finally', 'with', 'as', 'return',
            'len', 'range', 'list', 'dict', 'tuple', 'set', 'str', 'int', 
            'float', 'bool', 'type', 'isinstance', 'hasattr', 'getattr'
        ]
        
        # Common bash commands for completion
        self.bash_commands = [
            'ls', 'cd', 'pwd', 'mkdir', 'rmdir', 'rm', 'cp', 'mv', 'find',
            'grep', 'cat', 'head', 'tail', 'less', 'more', 'nano', 'vim',
            'git', 'docker', 'python', 'pip', 'npm', 'node', 'code', 'ssh'
        ]
        
        # Model configuration commands
        self.model_commands = [
            'status', 'set', 'mode', 'available'
        ]
        
        # Available models
        self.model_names = ['claude', 'gemini']
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        # Complete NEXUS command prefixes
        if not text or text.isspace():
            for cmd in self.nexus_commands:
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text))
        
        # Complete Python keywords after >
        elif text.startswith('>'):
            python_code = text[1:].strip()
            last_word = python_code.split()[-1] if python_code.split() else ''
            
            for keyword in self.python_keywords:
                if keyword.startswith(last_word):
                    yield Completion(keyword, start_position=-len(last_word))
        
        # Complete bash commands after !
        elif text.startswith('!') and not text.startswith('!i ') and not text.startswith('!c '):
            bash_command = text[1:].strip()
            last_word = bash_command.split()[-1] if bash_command.split() else bash_command
            
            for cmd in self.bash_commands:
                if cmd.startswith(last_word):
                    yield Completion(cmd, start_position=-len(last_word))
        
        # Complete model commands after 'model '
        elif text.startswith('model '):
            model_command = text[6:].strip()
            
            for cmd in self.model_commands:
                if cmd.startswith(model_command):
                    yield Completion(cmd, start_position=-len(model_command))
            
            # If 'model set ' is typed, complete with model names
            if text.startswith('model set '):
                model_name = text[10:].strip()
                for model in self.model_names:
                    if model.startswith(model_name):
                        yield Completion(model, start_position=-len(model_name))
        
        # Complete model names for direct model commands
        elif any(text.startswith(model + ' ') for model in self.model_names):
            # Already has model name, don't add more completions for now
            pass


class NexusPromptToolkitREPL:
    """Main REPL class using prompt_toolkit"""
    
    def __init__(self, session: Optional[Session] = None, 
                 default_model: ModelType = ModelType.CLAUDE, 
                 default_mode: ExecutionMode = ExecutionMode.LOCAL):
        # Initialize session and components
        self.session = session or Session()
        self.executor = CodeExecutor(self.session)
        self.output_manager = self.session.output_manager
        
        # Initialize model factory and backward compatibility
        self.model_factory = model_factory
        
        # Initialize legacy Claude client for backward compatibility
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.claude_client = ClaudeClient(api_key)
        else:
            self.claude_client = None
            # Only show warning if user is trying to use Claude API
            if default_model == ModelType.CLAUDE and default_mode == ExecutionMode.API:
                print("Warning: ANTHROPIC_API_KEY not found. Claude API mode will be unavailable.")
                print("Consider using --model claude-local for local execution.")
        
        # Current mode tracking for dynamic features
        self.current_mode = "nexus"
        self.last_input = ""
        
        # Default model settings from CLI arguments
        self.default_model = default_model
        self.default_execution_mode = default_mode
        
        # Set factory defaults to match CLI selection
        self.model_factory.set_default_model(default_model)
        self.model_factory.set_default_mode(default_mode)
        
        # Create prompt session with rich features
        self.prompt_session = PromptSession(
            history=FileHistory(os.path.expanduser('~/.nexus_history')),
            auto_suggest=AutoSuggestFromHistory(),
            completer=NexusCompleter(),
            style=self.create_style(),
            multiline=False,  # We'll handle multiline manually
            prompt_continuation="... ",
            enable_system_prompt=True,
            enable_suspend=True,
            enable_open_in_editor=True,
            bottom_toolbar=self.get_bottom_toolbar,
        )
    
    def create_style(self) -> Style:
        """Create custom style for NEXUS"""
        return Style.from_dict({
            # Token colors
            'prompt': '#00aa00 bold',
            'continuation': '#888888',
            'command': '#ffffff',
            'output': '#aaaaaa',
            'error': '#ff0000 bold',
            
            # Syntax highlighting
            'pygments.keyword': '#0080ff bold',
            'pygments.string': '#00aa00',
            'pygments.comment': '#888888',
            'pygments.function': '#ffaa00',
            'pygments.number': '#ff6600',
            'pygments.operator': '#ffffff',
            
            # UI elements
            'bottom-toolbar': 'bg:#222222 #aaaaaa',
            'completion-menu': 'bg:#444444 #ffffff',
            'completion-menu.completion': '',
            'completion-menu.completion.current': 'bg:#666666 #ffffff bold',
        })
    
    def get_bottom_toolbar(self) -> List[tuple]:
        """Show session info in bottom toolbar"""
        outputs_count = len(self.session.output_history)
        session_id = self.session.session_id[:8] if self.session.session_id else "unknown"
        
        return [
            ('class:bottom-toolbar', 
             f' NEXUS | Session: {session_id} | '
             f'Outputs: {outputs_count} | '
             f'Mode: {self.current_mode} | '
             f'Ctrl+C: exit, Ctrl+D: EOF ')
        ]
    
    def print_intro(self):
        """Print the NEXUS introduction"""
        # Get current model info for display
        model_display = f"{self.default_model.value}-{self.default_execution_mode.value}"
        
        intro = f"""
    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    Neural EXecution and Understanding System v0.3.0
    
    Enhanced with prompt_toolkit - Full interactive support
    Default AI Model: {model_display}
    
    task: <description> - Start new task
    > <code>          - Python REPL
    ! <command>       - Bash REPL (auto-detect interactive)
    !i <command>      - Force interactive bash command
    !c <command>      - Force captured bash command
    ?? <query> or claude <query> - Ask AI (uses default model)
    help             - Show all commands"""
        print(intro)
    
    async def run(self):
        """Main async event loop"""
        self.print_intro()
        
        while True:
            try:
                # Get user input
                line = await self.get_input()
                
                if not line.strip():
                    continue
                
                # Update mode based on input
                self.update_mode(line)
                
                # Parse and execute command
                await self.parse_command(line)
                
            except EOFError:
                print("\nGoodbye!")
                break
            except KeyboardInterrupt:
                print("\nUse Ctrl+D or type 'exit' to quit")
                continue
            except Exception as e:
                print(f"Error: {str(e)}")
                continue
    
    async def get_input(self) -> str:
        """Get user input with proper async handling"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.prompt_session.prompt("🔮 ")
        )
    
    def update_mode(self, line: str):
        """Update current mode based on input"""
        self.last_input = line
        
        if line.startswith('>'):
            self.current_mode = "python"
        elif line.startswith('!'):
            self.current_mode = "bash"
        elif line.startswith('??') or line.startswith('claude') or line.startswith('gemini'):
            self.current_mode = "ai_model"
        elif line.startswith('model '):
            self.current_mode = "model_config"
        elif line.startswith('task:'):
            self.current_mode = "task"
        else:
            self.current_mode = "nexus"
    
    async def parse_command(self, line: str):
        """Parse and route commands to appropriate handlers"""
        
        # Strip and check for empty
        line = line.strip()
        if not line:
            return
        
        # Python execution with >
        if line.startswith('>'):
            code = line[1:].strip()
            await self.handle_python(code)
        
        # Interactive bash with !i
        elif line.startswith('!i '):
            command = line[3:].strip()
            await self.handle_bash_interactive(command)
        
        # Captured bash with !c
        elif line.startswith('!c '):
            command = line[3:].strip()
            await self.handle_bash_captured(command)
        
        # Auto-detect bash with !
        elif line.startswith('!'):
            command = line[1:].strip()
            await self.handle_bash(command)
        
        # Claude queries with ??
        elif line.startswith('??'):
            query = line[2:].strip()
            await self.handle_claude(query)
        
        # Claude local execution with -p flag
        elif line.startswith('claude -p '):
            query = line[10:].strip()
            await self.handle_model_query('claude', 'local', query)
        
        # Claude API (backward compatibility)
        elif line.startswith('claude '):
            query = line[7:].strip()
            await self.handle_claude(query)
        
        # Gemini local execution with -p flag  
        elif line.startswith('gemini -p '):
            query = line[10:].strip()
            await self.handle_model_query('gemini', 'local', query)
        
        # Gemini API execution
        elif line.startswith('gemini '):
            query = line[7:].strip()
            await self.handle_model_query('gemini', 'api', query)
        
        # Model configuration commands
        elif line.startswith('model '):
            await self.handle_model_config(line[6:].strip())
        
        # Task execution
        elif line.startswith('task:'):
            task = line[5:].strip()
            await self.handle_task(task)
        
        # Exit commands
        elif line in ('exit', 'quit', 'exit()', 'quit()'):
            raise EOFError
        
        # Help command
        elif line == 'help':
            self.show_help()
        
        # Default to bash
        else:
            await self.handle_bash(line)
    
    async def handle_python(self, code: str):
        """Execute Python code (synchronously for now)"""
        try:
            # Execute Python code using the existing executor
            stdout, stderr = self.executor.execute_python(code)
            
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            
            # Store output
            if stdout:
                self.output_manager.store_output("python_stdout", stdout)
            if stderr:
                self.output_manager.store_output("python_stderr", stderr)
                
        except Exception as e:
            error_msg = f"Error executing Python code: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.output_manager.store_output("python_error", error_msg)
    
    async def handle_bash(self, command: str):
        """Execute bash command with auto-detection"""
        try:
            # Use async subprocess handling
            stdout, stderr = await self.executor.execute_bash_async(command)
            
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            
            # Store output
            if stdout:
                self.output_manager.store_output("bash_stdout", stdout)
            if stderr:
                self.output_manager.store_output("bash_stderr", stderr)
                
        except Exception as e:
            error_msg = f"Error executing bash command: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.output_manager.store_output("bash_error", error_msg)
    
    async def handle_bash_interactive(self, command: str):
        """Force interactive mode for bash command"""
        try:
            # Use async subprocess handling with forced interactive mode
            stdout, stderr = await self.executor.execute_bash_async(command, mode='interactive')
            
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            
            # Store minimal output info for interactive commands
            self.output_manager.store_output("bash_interactive", f"Executed: {command}")
                
        except Exception as e:
            error_msg = f"Error in interactive mode: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.output_manager.store_output("bash_interactive_error", error_msg)
    
    async def handle_bash_captured(self, command: str):
        """Force captured mode for bash command"""
        try:
            # Use async subprocess handling with forced captured mode
            stdout, stderr = await self.executor.execute_bash_async(command, mode='captured')
            
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            
            # Store full output
            if stdout:
                self.output_manager.store_output("bash_stdout", stdout)
            if stderr:
                self.output_manager.store_output("bash_stderr", stderr)
                
        except Exception as e:
            error_msg = f"Error in captured mode: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.output_manager.store_output("bash_captured_error", error_msg)
    
    async def handle_claude(self, query: str):
        """Process Claude queries - uses the configured default model and mode"""
        try:
            # Get context from output manager
            context = self.output_manager.get_recent_context()
            
            # Use the default model and mode configured by the user
            try:
                model = self.model_factory.get_model()
                response = await model.get_response(query, context)
                model_name = model.name.title().replace('_', '-')
            except (ModelUnavailableError, ModelExecutionError) as e:
                # Fallback to legacy Claude client if default model fails and it's available
                if self.claude_client and self.default_model == ModelType.CLAUDE:
                    print(f"\nDefault model unavailable ({str(e)}), falling back to Claude API...")
                    response = self.claude_client.get_response(query, context)
                    model_name = "Claude-API"
                else:
                    raise ModelUnavailableError(f"Default model unavailable: {str(e)}")
            
            print(f"\n{model_name} response:")
            print(response)
            
            # Store response with model info
            self.output_manager.store_output(f"{model_name.lower().replace('-', '_')}_response", response)
            
        except ModelUnavailableError as e:
            print(f"\nError: {str(e)}")
            print(f"Tip: Check your default model settings with 'model status'")
        except BadRequestError as e:
            if "credit balance is too low" in str(e):
                print("\nError: Your Anthropic API credit balance is too low.")
                print("Please visit https://console.anthropic.com to manage your billing.")
                print("Tip: Use local execution instead!")
            else:
                print(f"\nError making request to API: {str(e)}")
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            print("Tip: Check your setup with 'model status'")
    
    async def handle_task(self, task: str):
        """Execute task with AI assistance using default model"""
        try:
            # Format task query
            task_query = f"Help me with this task: {task}"
            
            # Get context
            context = self.output_manager.get_recent_context()
            
            # Try to use the default model first
            try:
                model = self.model_factory.get_model()
                response = await model.get_response(task_query, context)
                model_name = model.name
            except (ModelUnavailableError, ModelExecutionError):
                # Fallback to legacy Claude client if default model fails
                if self.claude_client:
                    response = self.claude_client.get_response(task_query, context)
                    model_name = "claude-api"
                else:
                    raise Exception("No AI model available for task assistance")
            
            print(f"\n📋 Task: {task}")
            print(f"\n{model_name.title()} assistance:")
            print(response)
            
            # Store task and response
            self.output_manager.store_output("task", task)
            self.output_manager.store_output(f"{model_name}_task_response", response)
            
        except Exception as e:
            error_msg = f"Error processing task: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.output_manager.store_output("task_error", error_msg)
    
    async def handle_model_query(self, model_name: str, execution_mode: str, query: str):
        """Handle AI model queries with specified execution mode"""
        try:
            # Map execution mode string to enum
            mode = ExecutionMode.LOCAL if execution_mode == 'local' else ExecutionMode.API
            
            # Get model instance from factory
            model = self.model_factory.get_model(model_name, mode)
            
            # Get context from output manager
            context = self.output_manager.get_recent_context()
            
            # Get response from model
            response = await model.get_response(query, context)
            
            print(f"\n{model.name.title()} response:")
            print(response)
            
            # Store response
            self.output_manager.store_output(f"{model.name}_response", response)
            
        except ModelUnavailableError as e:
            error_msg = f"Model unavailable: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.output_manager.store_output("model_error", error_msg)
        except ModelExecutionError as e:
            error_msg = f"Model execution error: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.output_manager.store_output("model_error", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.output_manager.store_output("model_error", error_msg)
    
    async def handle_model_config(self, command: str):
        """Handle model configuration commands"""
        parts = command.split()
        
        if not parts:
            await self.show_model_status()
            return
        
        cmd = parts[0].lower()
        
        if cmd == 'status':
            await self.show_model_status()
        elif cmd == 'set' and len(parts) >= 2:
            await self.set_default_model(parts[1])
        elif cmd == 'mode' and len(parts) >= 2:
            await self.set_default_mode(parts[1])
        elif cmd == 'available':
            await self.show_available_models()
        else:
            print("Available model commands:")
            print("  model status         - Show current model settings")
            print("  model set <model>    - Set default model (claude/gemini)")
            print("  model mode <mode>    - Set default mode (local/api)")
            print("  model available      - Show available models")
    
    async def show_model_status(self):
        """Show current model configuration"""
        print(f"\nCurrent Model Settings:")
        print(f"  Default Model: {self.default_model.value}")
        print(f"  Default Mode: {self.default_execution_mode.value}")
        
        # Show availability
        availability = self.model_factory.get_available_models()
        print(f"\nModel Availability:")
        for model_name, modes in availability.items():
            print(f"  {model_name}:")
            for mode_name, available in modes.items():
                status = "✓" if available else "✗"
                print(f"    {mode_name}: {status}")
    
    async def set_default_model(self, model_name: str):
        """Set default model"""
        try:
            model_type = ModelType(model_name.lower())
            self.default_model = model_type
            self.model_factory.set_default_model(model_type)
            print(f"Default model set to: {model_name}")
        except ValueError:
            print(f"Unknown model: {model_name}. Available: claude, gemini")
    
    async def set_default_mode(self, mode_name: str):
        """Set default execution mode"""
        try:
            execution_mode = ExecutionMode(mode_name.lower())
            self.default_execution_mode = execution_mode
            self.model_factory.set_default_mode(execution_mode)
            print(f"Default execution mode set to: {mode_name}")
        except ValueError:
            print(f"Unknown mode: {mode_name}. Available: local, api")
    
    async def show_available_models(self):
        """Show detailed model availability"""
        availability = self.model_factory.get_available_models()
        print("\nDetailed Model Availability:")
        
        for model_name, modes in availability.items():
            print(f"\n{model_name.upper()}:")
            for mode_name, available in modes.items():
                status = "Available" if available else "Not Available"
                print(f"  {mode_name}: {status}")
                
                if available:
                    if mode_name == "local":
                        cmd = f"{model_name} -p"
                        print(f"    Usage: {cmd} <query>")
                    else:
                        print(f"    Usage: {model_name} <query>")
    
    def show_help(self):
        """Show help information"""
        model_display = f"{self.default_model.value}-{self.default_execution_mode.value}"
        
        help_text = f"""
Available Commands:
  > <code>           - Execute Python code
  ! <command>        - Execute bash command (auto-detect interactive)
  !i <command>       - Force interactive bash command  
  !c <command>       - Force captured bash command
  ?? <query>         - Ask AI (uses current default: {model_display})
  claude <query>     - Ask Claude (uses current default mode)  
  claude -p <query>  - Ask Claude (explicit local mode)
  gemini <query>     - Ask Gemini (API mode)
  gemini -p <query>  - Ask Gemini (local mode)
  model status       - Show model configuration
  model set <model>  - Set default model
  model mode <mode>  - Set default execution mode
  task: <description>- Start a new task
  help               - Show this help
  exit/quit          - Exit NEXUS

CLI Model Selection (restart NEXUS with these flags):
  nexus --model claude-local    - Start with Claude local execution
  nexus --model claude-api      - Start with Claude API
  nexus --model gemini-local    - Start with Gemini local execution
  nexus --model gemini-api      - Start with Gemini API

Examples:
  > print("Hello World")
  !i ssh user@server
  !c ls -la
  ?? how do I list files recursively?
  task: analyze the current directory structure

Special Features:
  - Auto-completion with Tab
  - Command history with Up/Down arrows
  - Multi-line support for complex commands
  - Real-time output for interactive commands
  - Bottom toolbar shows session information
  - CLI model selection on startup
"""
        print(help_text)