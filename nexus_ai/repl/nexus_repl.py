# nexus-ai/nexus_ai/repl/nexus_repl.py

from nexus_ai.repl.base import BaseREPL
# from nexus_ai.core.session import Session
# from nexus_ai.core.executor import CodeExecutor
# from nexus_ai.claude.client import ClaudeClient


class NexusREPL(BaseREPL):
    intro = """
    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    Neural EXecution and Understanding System v0.1.0
    
    task: <description> - Start new task
    > <code>          - Python REPL
    ! <command>       - Bash REPL
    ?? <query> or claude <query> - Ask Claude
    help             - Show all commands"""

    prompt = "🔮 "

    def __init__(self):
        super().__init__()

    def preloop(self):
        """Print intro on startup"""
        return super().preloop()
