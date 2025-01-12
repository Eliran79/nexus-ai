# nexus-ai/nexus_ai/core/session.py
from datetime import datetime
from typing import Dict
import time

from nexus_ai.core.output import OutputManager


class Session:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self.start_time = datetime.now()
        self.python_locals = {}
        self.python_globals = {}
        self.output_history = []
        self.execution_history = []
        self.task_status = {}
        self.user_inputs = {}
        self.subtasks = []
        self.metadata = {
            "created_at": self.start_time,
            "last_modified": self.start_time,
            "tasks_completed": 0,
            "description": "",
            "tags": [],
        }
        self.output_manager = OutputManager(self)

    def add_output(self, output_type: str, content: str):
        """Add output to history"""
        self.output_history.append(
            {"timestamp": datetime.now(), "type": output_type, "content": content}
        )
        self.metadata["last_modified"] = datetime.now()

    def to_dict(self) -> Dict:
        """Convert session to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "output_history": self.output_history,
            "execution_history": self.execution_history,
            "task_status": self.task_status,
            "user_inputs": self.user_inputs,
            "subtasks": self.subtasks,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Session":
        """Create session from dictionary"""
        session = cls(data["session_id"])
        session.__dict__.update(data)
        return session
