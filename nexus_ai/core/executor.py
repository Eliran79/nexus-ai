# nexus-ai/nexus_ai/core/executor.py

import sys
import subprocess
from typing import Tuple
from nexus_ai.core.output import CaptureOutput


class CodeExecutor:
    def __init__(self, session):
        self.session = session
        self.output_manager = session.output_manager

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

    def execute_bash(self, command: str) -> Tuple[str, str]:
        """Execute bash command and capture output"""
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            return result.stdout, result.stderr
        except Exception as e:
            return "", str(e)
