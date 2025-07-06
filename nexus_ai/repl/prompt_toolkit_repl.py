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
            'claude ',  # Claude query
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


class NexusPromptToolkitREPL:
    """Main REPL class using prompt_toolkit"""
    
    def __init__(self, session: Optional[Session] = None):
        # Initialize session and components
        self.session = session or Session()
        self.executor = CodeExecutor(self.session)
        self.output_manager = self.session.output_manager
        
        # Initialize Claude client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not found")
            print("Please set your API key before running nexus-ai")
            sys.exit(1)
        
        self.claude_client = ClaudeClient(api_key)
        
        # Current mode tracking for dynamic features
        self.current_mode = "nexus"
        self.last_input = ""
        
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
        intro = """
    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    Neural EXecution and Understanding System v0.2.0
    
    Enhanced with prompt_toolkit - Full interactive support
    
    task: <description> - Start new task
    > <code>          - Python REPL
    ! <command>       - Bash REPL (auto-detect interactive)
    !i <command>      - Force interactive bash command
    !c <command>      - Force captured bash command
    ?? <query> or claude <query> - Ask Claude
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
        elif line.startswith('??') or line.startswith('claude'):
            self.current_mode = "claude"
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
        
        # Claude with explicit command
        elif line.startswith('claude '):
            query = line[7:].strip()
            await self.handle_claude(query)
        
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
        """Process Claude queries"""
        try:
            # Get context from output manager
            context = self.output_manager.get_recent_context()
            
            # Get response from Claude
            response = self.claude_client.get_response(query, context)
            
            print("\nClaude's response:")
            print(response)
            
            # Store Claude response
            self.output_manager.store_output("claude", response)
            
        except BadRequestError as e:
            if "credit balance is too low" in str(e):
                print("\nError: Your Anthropic API credit balance is too low.")
                print("Please visit https://console.anthropic.com to manage your billing.")
            else:
                print(f"\nError making request to Claude: {str(e)}")
        except Exception as e:
            print(f"\nUnexpected error when talking to Claude: {str(e)}")
    
    async def handle_task(self, task: str):
        """Execute task with Claude assistance"""
        try:
            # Format task query for Claude
            task_query = f"Help me with this task: {task}"
            
            # Get context and response
            context = self.output_manager.get_recent_context()
            response = self.claude_client.get_response(task_query, context)
            
            print(f"\n📋 Task: {task}")
            print("\nClaude's assistance:")
            print(response)
            
            # Store task and response
            self.output_manager.store_output("task", task)
            self.output_manager.store_output("claude_task_response", response)
            
        except Exception as e:
            error_msg = f"Error processing task: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.output_manager.store_output("task_error", error_msg)
    
    def show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
  > <code>           - Execute Python code
  ! <command>        - Execute bash command (auto-detect interactive)
  !i <command>       - Force interactive bash command  
  !c <command>       - Force captured bash command
  ?? <query>         - Ask Claude for assistance
  claude <query>     - Ask Claude for assistance
  task: <description>- Start a new task
  help               - Show this help
  exit/quit          - Exit NEXUS

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
"""
        print(help_text)