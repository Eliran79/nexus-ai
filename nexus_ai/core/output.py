# nexus-ai/nexus_ai/core/output.py
import sys
from io import StringIO
from typing import Tuple
from datetime import datetime


class CaptureOutput:
    """Capture stdout and stderr"""

    def __init__(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def __enter__(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        return self

    def __exit__(self, *args):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

    def get_output(self) -> Tuple[str, str]:
        return self.stdout.getvalue(), self.stderr.getvalue()


class OutputManager:
    def __init__(self, session):
        self._session = session  # Use _session to avoid confusion
        self.max_history = 1000

    def store_output(self, output_type: str, content: str):
        """Store output with timestamp"""
        self._session.output_history.append(
            {"timestamp": datetime.now(), "type": output_type, "content": content}
        )

        # Trim history if too long
        if len(self._session.output_history) > self.max_history:
            self._session.output_history = self._session.output_history[
                -self.max_history :
            ]

    def get_recent_context(self, limit: int = 10) -> str:
        """Get recent output context"""
        recent = (
            self._session.output_history[-limit:]
            if self._session.output_history
            else []
        )
        return "\n".join(
            f"[{o['timestamp']}] {o['type']}: {o['content']}" for o in recent
        )
