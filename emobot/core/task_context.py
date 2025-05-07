# emobot/core/task_context.py
import json
import os
from typing import List, Dict, Any

class TaskContext:
    """Manages todo task context for the MCP approach."""
    
    def __init__(self, user_id: str):
        """Initialize task context for a specific user."""
        self.user_id = user_id
        self.tasks_file = f"data/user_data/{user_id}_tasks.json"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create tasks file if it doesn't exist."""
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
        if not os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'w') as f:
                json.dump({"tasks": []}, f)
    
    def get_tasks_context(self) -> str:
        """Get current tasks as a formatted context string for the LLM."""
        tasks = self._load_tasks()
        
        if not tasks:
            return "You currently have no tasks in your todo list."
        
        tasks_text = "Your current tasks:\n"
        for i, task in enumerate(tasks, 1):
            status = "✓" if task.get("completed", False) else "□"
            tasks_text += f"{i}. {status} {task['title']}"
            if task.get("due_date"):
                tasks_text += f" (Due: {task['due_date']})"
            tasks_text += "\n"
        
        return tasks_text
    
    def _load_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks from file."""
        with open(self.tasks_file, 'r') as f:
            data = json.load(f)
        return data.get("tasks", [])
    
    def save_tasks(self, tasks: List[Dict[str, Any]]):
        """Save tasks to file."""
        with open(self.tasks_file, 'w') as f:
            json.dump({"tasks": tasks}, f)
    
    def execute_task_action(self, llm_action: str) -> str:
        """Execute a task action interpreted by the LLM."""
        # Parse the action from LLM response
        action_lines = llm_action.strip().split('\n')
        action_type = action_lines[0].lower() if action_lines else ""
        
        tasks = self._load_tasks()
        
        if "add task" in action_type:
            # Format: add task: title | due_date (optional)
            parts = action_type.replace("add task:", "").split("|")
            title = parts[0].strip()
            due_date = parts[1].strip() if len(parts) > 1 else None
            
            tasks.append({
                "title": title,
                "completed": False,
                "due_date": due_date
            })
            self.save_tasks(tasks)
            return f"Added task: {title}"
            
        elif "complete task" in action_type:
            # Format: complete task: index or title
            task_id = action_type.replace("complete task:", "").strip()
            
            # Check if task_id is a number (index) or text (title)
            try:
                task_index = int(task_id) - 1
                if 0 <= task_index < len(tasks):
                    tasks[task_index]["completed"] = True
                    self.save_tasks(tasks)
                    return f"Marked task '{tasks[task_index]['title']}' as completed."
            except ValueError:
                # Search by title
                for task in tasks:
                    if task_id.lower() in task["title"].lower():
                        task["completed"] = True
                        self.save_tasks(tasks)
                        return f"Marked task '{task['title']}' as completed."
            
            return "Task not found."
            
        elif "delete task" in action_type:
            # Format: delete task: index or title
            task_id = action_type.replace("delete task:", "").strip()
            
            try:
                task_index = int(task_id) - 1
                if 0 <= task_index < len(tasks):
                    deleted_task = tasks.pop(task_index)
                    self.save_tasks(tasks)
                    return f"Deleted task: {deleted_task['title']}"
            except ValueError:
                # Search by title
                for i, task in enumerate(tasks):
                    if task_id.lower() in task["title"].lower():
                        deleted_task = tasks.pop(i)
                        self.save_tasks(tasks)
                        return f"Deleted task: {deleted_task['title']}"
            
            return "Task not found."
            
        elif "list tasks" in action_type:
            return self.get_tasks_context()
            
        else:
            return "I didn't understand that task action."