"""
Emobot Agent 模块

Intelligent assistant based on smolagents framework, containing the following core components:
- Perception Module: Process and understand user input
- Reasoning Module: Implements ReAct loop for thinking and decision making
- Memory Module: Manage short-term and long-term memory
- Actions Module: Execute specific tool calls and actions
"""

from .perception import PerceptionModule
from .reasoning import ReasoningModule
from .memory import MemoryManager
from .actions import ActionExecutor

__all__ = [
    "PerceptionModule",
    "ReasoningModule", 
    "MemoryManager",
    "ActionExecutor"
]

__version__ = "1.0.0"
