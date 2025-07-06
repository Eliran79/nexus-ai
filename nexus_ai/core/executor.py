# nexus-ai/nexus_ai/core/executor.py

import sys
import subprocess
import asyncio
import pty
import os
import select
import termios
import tty
from typing import Tuple, Optional
from nexus_ai.core.output import CaptureOutput


class CodeExecutor:
    def __init__(self, session):
        self.session = session
        self.output_manager = session.output_manager
        
        # Interactive command patterns
        self.interactive_commands = {
            'ssh', 'scp', 'ftp', 'sftp', 'telnet', 
            'mysql', 'psql', 'mongo', 'redis-cli',
            'docker', 'kubectl', 'vim', 'nano', 'emacs',
            'less', 'more', 'man', 'top', 'htop', 'watch',
            'tail', 'git', 'sudo', 'passwd', 'su', 'login',
            'python', 'python3', 'ipython', 'node', 'npm',
            'pip', 'apt', 'yum', 'brew', 'conda', 'yay',
            'pacman', 'paru', 'makepkg', 'aurman'
        }
        
        # Background commands (return immediately)
        self.background_commands = {
            'code', 'subl', 'atom', 'gedit', 'xdg-open',
            'open', 'explorer', 'firefox', 'chrome'
        }

    def execute_python(self, code: str) -> Tuple[str, str]:
        """Execute Python code and capture output"""
        with CaptureOutput() as output:
            try:
                # Try to eval first
                try:
                    result = eval(
                        code, self.session.python_globals, self.session.python_locals
                    )
                    if result is not None:
                        print(result)
                except SyntaxError:
                    # If not an expression, execute as statement
                    exec(code, self.session.python_globals, self.session.python_locals)
            except Exception as e:
                print(f"Error: {str(e)}", file=sys.stderr)

        return output.get_output()

    def is_likely_interactive(self, command: str) -> bool:
        """Detect if a command is likely to be interactive"""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
            
        base_command = cmd_parts[0].split('/')[-1]  # Handle full paths
        
        # Check if it's a known interactive command
        if base_command in self.interactive_commands:
            return True
            
        # Check for interactive flags
        interactive_flags = ['-i', '--interactive', '-it', '--stdin']
        if any(flag in cmd_parts for flag in interactive_flags):
            return True
            
        # Check for input redirection or pipes that might indicate non-interactive
        if any(symbol in command for symbol in ['<', '>', '>>', '|']):
            return False
            
        return False
    
    def _is_background_command(self, command: str) -> bool:
        """Check if command should run in background"""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
            
        base_command = cmd_parts[0].split('/')[-1]
        return base_command in self.background_commands
    
    def _is_interactive_command(self, command: str) -> bool:
        """Check if command is interactive"""
        return self.is_likely_interactive(command)
    
    def execute_bash(self, command: str) -> Tuple[str, str]:
        """Execute bash command with interactive support"""
        # Check if command is likely interactive
        if self.is_likely_interactive(command):
            return self._execute_interactive_bash(command)
        else:
            return self._execute_captured_bash(command)
    
    def _execute_interactive_bash(self, command: str) -> Tuple[str, str]:
        """Execute interactive bash command using PTY for proper terminal emulation"""
        try:
            print(f"🔄 Running interactive command: {command}")
            
            # Create master and slave PTY
            master_fd, slave_fd = pty.openpty()
            
            # Fork a child process
            pid = os.fork()
            
            if pid == 0:  # Child process
                # Close master in child
                os.close(master_fd)
                
                # Make slave the controlling terminal
                os.setsid()
                os.dup2(slave_fd, 0)  # stdin
                os.dup2(slave_fd, 1)  # stdout
                os.dup2(slave_fd, 2)  # stderr
                
                # Close the original slave fd
                if slave_fd > 2:
                    os.close(slave_fd)
                
                # Execute the command
                os.execv('/bin/bash', ['/bin/bash', '-c', command])
                
            else:  # Parent process
                # Close slave in parent
                os.close(slave_fd)
                
                # Save terminal settings and set to raw mode
                old_tty = termios.tcgetattr(sys.stdin)
                try:
                    tty.setraw(sys.stdin.fileno())
                    
                    # Forward data between terminal and PTY
                    while True:
                        try:
                            # Check for data from PTY or stdin
                            r, _, _ = select.select([master_fd, sys.stdin], [], [], 0.01)
                            
                            if master_fd in r:
                                # Read from PTY and write to stdout
                                data = os.read(master_fd, 1024)
                                if not data:
                                    break
                                os.write(sys.stdout.fileno(), data)
                                
                            if sys.stdin in r:
                                # Read from stdin and write to PTY
                                data = os.read(sys.stdin.fileno(), 1024)
                                if not data:
                                    break
                                os.write(master_fd, data)
                                
                            # Check if child process has exited
                            wpid, status = os.waitpid(pid, os.WNOHANG)
                            if wpid == pid:
                                # Read any remaining output
                                while True:
                                    try:
                                        data = os.read(master_fd, 1024)
                                        if data:
                                            os.write(sys.stdout.fileno(), data)
                                        else:
                                            break
                                    except:
                                        break
                                break
                                
                        except (OSError, IOError):
                            break
                            
                except KeyboardInterrupt:
                    # Kill the child process on Ctrl+C
                    os.kill(pid, 9)
                    os.waitpid(pid, 0)
                    return "", "✗ Command interrupted by user"
                finally:
                    # Restore terminal settings
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
                    os.close(master_fd)
                
                # Get exit status
                _, status = os.waitpid(pid, 0)
                exit_code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1
                
                if exit_code == 0:
                    return "✓ Command completed successfully", ""
                else:
                    return "", f"✗ Command failed with exit code {exit_code}"
                    
        except Exception as e:
            return "", f"Error: {str(e)}"
    
    def _execute_captured_bash(self, command: str) -> Tuple[str, str]:
        """Execute non-interactive bash command with output capture"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                text=True, 
                capture_output=True,
                timeout=30  # Add timeout for safety
            )
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return "", f"Command timed out after 30 seconds"
        except Exception as e:
            return "", str(e)
    
    def force_interactive_mode(self, command: str) -> Tuple[str, str]:
        """Force a command to run in interactive mode"""
        return self._execute_interactive_bash(command)
    
    def force_captured_mode(self, command: str) -> Tuple[str, str]:
        """Force a command to run in captured mode"""
        return self._execute_captured_bash(command)
    
    async def execute_bash_async(self, command: str, 
                                mode: Optional[str] = None) -> Tuple[str, str]:
        """Execute bash command with auto-detection or forced mode"""
        
        # Determine execution mode
        if mode == 'interactive':
            return await self._execute_interactive_async(command)
        elif mode == 'captured':
            return await self._execute_captured_async(command)
        elif mode == 'background':
            return await self._execute_background_async(command)
        else:
            # Auto-detect mode
            if self._is_background_command(command):
                return await self._execute_background_async(command)
            elif self._is_interactive_command(command):
                return await self._execute_interactive_async(command)
            else:
                return await self._execute_captured_async(command)
    
    async def _execute_interactive_async(self, command: str) -> Tuple[str, str]:
        """Execute with full terminal interaction using PTY"""
        print(f"🔄 Running interactive: {command}")
        
        # For the async version, we'll use a simpler approach that delegates
        # to the synchronous implementation to avoid issues with async terminal handling
        loop = asyncio.get_event_loop()
        
        try:
            # Run the synchronous version in a thread pool to avoid blocking
            result = await loop.run_in_executor(
                None,
                self._execute_interactive_bash,
                command
            )
            return result
            
        except Exception as e:
            return "", f"Error: {str(e)}"
    
    async def _execute_captured_async(self, command: str) -> Tuple[str, str]:
        """Execute with output capture for analysis"""
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE
        )
        
        # Collect output with real-time display option
        stdout_lines = []
        stderr_lines = []
        
        # Read stdout
        if process.stdout:
            async for line in process.stdout:
                decoded = line.decode('utf-8', errors='replace')
                stdout_lines.append(decoded)
                print(decoded, end='')  # Real-time display
        
        # Read stderr
        if process.stderr:
            async for line in process.stderr:
                decoded = line.decode('utf-8', errors='replace')
                stderr_lines.append(decoded)
                print(decoded, end='', file=sys.stderr)
        
        await process.wait()
        
        return ''.join(stdout_lines), ''.join(stderr_lines)
    
    async def _execute_background_async(self, command: str) -> Tuple[str, str]:
        """Execute in background (like editors)"""
        
        await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
            stdin=asyncio.subprocess.DEVNULL
        )
        
        # Don't wait - return immediately
        return f"✓ Launched in background: {command}", ""
