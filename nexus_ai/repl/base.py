# nexus-ai/nexus_ai/repl/base.py
import re
from typing import List, Tuple
import cmd
import os
import sys
from nexus_ai.core.session import Session
from nexus_ai.core.executor import CodeExecutor
from nexus_ai.claude.client import ClaudeClient
from anthropic import BadRequestError


class BaseREPL(cmd.Cmd):
    intro = """Task Execution Agent
    task: <description> - Start new task
    > <code>          - Python REPL
    ! <command>       - Bash REPL
    ? <query>         - Ask Claude
    help             - Show all commands"""

    prompt = "📋 "

    def __init__(self):
        super().__init__()
        self.session = Session()
        self.executor = CodeExecutor(self.session)

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not found")
            print("Please set your API key before running nexus-ai")
            sys.exit(1)

        self.claude = ClaudeClient(api_key)

    def default(self, line: str):
        """Handle different command types"""
        try:
            if line.startswith("??"):
                # Handle Claude queries
                query = line[2:].strip()
                if query:
                    self.handle_claude(query)
                else:
                    print("Please provide a query after ??")

            elif line.startswith("claude "):
                # Handle Claude queries with 'claude' prefix
                query = line[7:].strip()
                if query:
                    self.handle_claude(query)
                else:
                    print("Please provide a query after 'claude'")

            elif line.startswith(">"):
                # Handle Python with > prefix
                code = line[1:].strip()
                if code:
                    self.handle_python(code)
                else:
                    print("Please provide Python code after '>'")

            elif line.startswith("!"):
                # Handle explicit bash commands
                command = line[1:].strip()
                if command:
                    self.handle_bash(command)
                else:
                    print("Please provide a command after '!'")

            elif line.startswith("task:"):
                # Handle task execution
                task = line[5:].strip()
                if task:
                    self.handle_task(task)
                else:
                    print("Please provide a task description after 'task:'")

            elif line in ("exit", "exit()", "quit", "quit()"):
                # Handle exit commands
                return self.do_exit(None)

            else:
                # Default to bash execution for bare commands
                self.handle_bash(line)

        except Exception as e:
            print(f"Error: {str(e)}")

    def handle_task(self, task: str):
        raise NotImplementedError

    def handle_python(self, code: str):
        """Handle Python code execution"""
        stdout, stderr = self.executor.execute_python(code)
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        # Store output
        if stdout:
            self.session.output_manager.store_output("python_stdout", stdout)
        if stderr:
            self.session.output_manager.store_output("python_stderr", stderr)

    def handle_bash(self, command: str):
        """Handle bash command execution"""
        stdout, stderr = self.executor.execute_bash(command)
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        # Store output
        if stdout:
            self.session.output_manager.store_output("bash_stdout", stdout)
        if stderr:
            self.session.output_manager.store_output("bash_stderr", stderr)

    def handle_claude(self, query: str):
        """Handle Claude interaction with improved error handling"""
        try:
            context = self.session.output_manager.get_recent_context()
            response = self.claude.get_response(query, context)
            print("\nClaude's response:")
            print(response)

            # Extract and handle commands
            commands = self.extract_commands(response)
            if commands:
                self.prompt_command_execution(commands)

            self.session.output_manager.store_output("claude", response)
        except BadRequestError as e:
            if "credit balance is too low" in str(e):
                print("\nError: Your Anthropic API credit balance is too low.")
                print(
                    "Please visit https://console.anthropic.com to manage your billing."
                )
            else:
                print(f"\nError making request to Claude: {str(e)}")
        except Exception as e:
            print(f"\nUnexpected error when talking to Claude: {str(e)}")

    def extract_commands(self, response: str) -> List[Tuple[str, str]]:
        """Extract commands from Claude's response"""
        commands = []
        seen_commands = set()

        # Extract Python code blocks (keeping indentation)
        code_blocks = []
        current_block = []
        in_block = False

        for line in response.split("\n"):
            if line.strip().startswith("```python"):
                in_block = True
                continue
            elif line.strip() == "```" and in_block:
                in_block = False
                if current_block:
                    code_blocks.append("\n".join(current_block))
                    current_block = []
                continue
            elif in_block:
                current_block.append(line)

        # Add complete Python blocks
        for block in code_blocks:
            if block.strip():
                commands.append(("python_block", block.strip()))

        # Extract inline Python commands
        python_lines = re.findall(r">[^\n]*\n?", response)
        for line in python_lines:
            command = line[1:].strip()
            if command:
                commands.append(("python", command))

        # Extract bash commands (excluding comments and explanations)
        bash_commands = re.findall(r"!(.*?)(?=\n|$)", response)
        for command in bash_commands:
            command = command.strip()
            if command and not command.startswith("#"):
                commands.append(("bash", command))

       # Deduplicate commands while preserving order
        unique_commands = []
        for command_type, command in commands:
            command_key = (command_type, command)
            if command_key not in seen_commands:
                seen_commands.add(command_key)
                unique_commands.append(command_key)
        
        return unique_commands

    def prompt_command_execution(self, commands: List[Tuple[str, str]]) -> None:
        """Prompt user for command execution"""
        if not commands:
            return

        print("\nDetected commands:")
        for idx, (command_type, command) in enumerate(commands, 1):
            print(f"{idx}. [{command_type}] {command}")

        while True:
            choice = (
                input("\nEnter command number to execute (or 'all'/'none'): ")
                .strip()
                .lower()
            )

            if choice == "none":
                break
            elif choice == "all":
                for command_type, command in commands:
                    self.execute_command(command_type, command)
                break
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(commands):
                        command_type, command = commands[idx]
                        self.execute_command(command_type, command)
                    else:
                        print("Invalid command number")
                except ValueError:
                    print("Please enter a valid number, 'all', or 'none'")

    def execute_command(self, command_type: str, command: str):
        """Execute a command based on its type"""
        print(f"\nExecuting {command_type} command: {command}")
        try:
            if command_type == "bash":
                # Expand home directory
                command = os.path.expanduser(command)
                self.handle_bash(command)
            elif command_type == "python_block":
                # Execute multi-line Python code
                exec(command, self.session.python_globals, self.session.python_locals)
                # Show updated variables
                vars_str = ", ".join(
                    f"{k}={v}"
                    for k, v in self.session.python_locals.items()
                    if not k.startswith("_")
                )
                if vars_str:
                    print(f"Python variables: {vars_str}")
            elif command_type == "python":
                # Execute single-line Python command
                try:
                    result = eval(
                        command, self.session.python_globals, self.session.python_locals
                    )
                    if result is not None:
                        print(result)
                except SyntaxError:
                    # If eval fails, try exec
                    exec(
                        command, self.session.python_globals, self.session.python_locals
                    )
        except Exception as e:
            print(f"Error executing {command_type} command: {e}")

    def do_help(self, arg):
        """Override default help to handle ? prefix"""
        if arg.startswith("?"):
            self.handle_claude(arg[1:].strip())
        else:
            super().do_help(arg)

    def do_exit(self, arg):
        """Exit the REPL"""
        print("\nGoodbye!")
        exit()
