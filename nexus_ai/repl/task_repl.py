# nexus-ai/nexus_ai/repl/task_repl.py
from typing import Dict, List
from nexus_ai.core.session import Session
from nexus_ai.claude.client import ClaudeClient


class TaskREPL:
    """Standalone task execution utilities"""
    
    def __init__(self, session=None):
        self.session = session or Session()
        self.claude_client = ClaudeClient()
    
    def handle_task_breakdown(self, task: str):
        """Handle task execution with breakdown into subtasks"""
        print(f"\n🎯 Starting new task: {task}")

        # Get task breakdown from Claude
        response = self.claude_client.get_response(
            f"Break down this task into clear, actionable subtasks: {task}",
            context=self.session.output_manager.get_recent_context(),
        )

        print(f"\n📋 Task breakdown:\n{response}")
        
        # Store the task and breakdown
        self.session.output_manager.store_output("task", task)
        self.session.output_manager.store_output("task_breakdown", response)
        
        return response

    def parse_subtasks(self, response: str) -> List[Dict]:
        """Parse Claude's response into subtasks"""
        # Basic implementation - extract numbered items
        lines = response.split('\n')
        subtasks = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                subtasks.append({
                    'description': line,
                    'completed': False
                })
        
        return subtasks

    def execute_subtasks(self, subtasks: List[Dict]):
        """Interactive subtask execution"""
        print("\n📝 Subtasks to complete:")
        
        for i, subtask in enumerate(subtasks, 1):
            print(f"{i}. {subtask['description']}")
        
        print("\nYou can now work through these subtasks in NEXUS.")
        print("Use 'task: <description>' for help with specific subtasks.")
