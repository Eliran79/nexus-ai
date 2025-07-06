# nexus-ai/nexus_ai/repl/python_repl.py
import sys
import code
from nexus_ai.core.session import Session


class PythonREPL:
    """Standalone Python REPL utilities"""
    
    def __init__(self, session=None):
        self.session = session or Session()
    
    def start_interactive_python(self):
        """Start interactive Python REPL"""
        print("Starting Python REPL (use 'exit()' to return)")
        print("Variables from your NEXUS session are available.")
        
        # Create a namespace with session variables
        namespace = {
            **self.session.python_globals,
            **self.session.python_locals
        }
        
        code.interact(local=namespace)
        
        # Update session with any new variables
        self.session.python_locals.update(namespace)
