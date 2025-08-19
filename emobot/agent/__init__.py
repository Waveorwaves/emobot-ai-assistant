"""
Emobot Agent 模块

基于 smolagents 框架实现的智能助手，包含以下核心组件：
- 感知模块 (Perception)：处理和理解用户输入
- 推理模块 (Reasoning)：实现 ReAct 循环，进行思考和决策
- 记忆模块 (Memory)：管理短期和长期记忆
- 动作模块 (Actions)：执行具体的工具调用和动作
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
