# nexus-ai/nexus_ai/repl/python_repl.py
import sys
from nexus_ai.repl.base import BaseREPL
import code


class PythonREPL(BaseREPL):
    def handle_python(self, code: str):
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

    def do_python(self, arg):
        """Start interactive Python REPL"""
        print("Starting Python REPL (use 'exit()' to return)")
        code.interact(local=self.session.python_locals)
