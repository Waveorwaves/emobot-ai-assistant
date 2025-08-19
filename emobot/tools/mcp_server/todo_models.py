#!/usr/bin/env python3
"""
待办事项数据模型和存储管理
"""
import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskCategory(Enum):
    """任务分类枚举"""
    WORK = "work"
    PERSONAL = "personal"
    STUDY = "study"
    HEALTH = "health"
    SHOPPING = "shopping"
    OTHER = "other"

class TodoTask:
    """待办事项类"""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        category: TaskCategory = TaskCategory.OTHER,
        due_date: Optional[str] = None,
        tags: List[str] = None,
        task_id: Optional[str] = None
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority
        self.category = category
        self.status = TaskStatus.PENDING
        self.due_date = due_date
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.completed_at = None
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "category": self.category.value,
            "status": self.status.value,
            "due_date": self.due_date,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoTask':
        """从字典创建任务对象"""
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            priority=TaskPriority(data["priority"]),
            category=TaskCategory(data["category"]),
            due_date=data.get("due_date"),
            tags=data.get("tags", []),
            task_id=data["task_id"]
        )
        task.status = TaskStatus(data["status"])
        task.created_at = data["created_at"]
        task.updated_at = data["updated_at"]
        task.completed_at = data.get("completed_at")
        return task
    
    def update(self, **kwargs):
        """更新任务属性"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
    
    def mark_completed(self):
        """标记任务为完成"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        self.updated_at = self.completed_at
    
    def is_overdue(self) -> bool:
        """检查任务是否逾期"""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return False
        try:
            due = datetime.fromisoformat(self.due_date).date()
            return due < date.today()
        except:
            return False
    
    def get_priority_score(self) -> int:
        """获取优先级分数（用于排序）"""
        priority_scores = {
            TaskPriority.LOW: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.HIGH: 3,
            TaskPriority.URGENT: 4
        }
        return priority_scores.get(self.priority, 2)

class TodoListManager:
    """待办事项列表管理器"""
    
    def __init__(self, storage_file: str = "todo_list.json"):
        self.storage_file = storage_file
        self.tasks: List[TodoTask] = []
        self.load_tasks()
    
    def load_tasks(self):
        """从文件加载任务"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [TodoTask.from_dict(task_data) for task_data in data]
            except Exception as e:
                print(f"加载待办事项失败: {e}")
                self.tasks = []
        else:
            self.tasks = []
    
    def save_tasks(self):
        """保存任务到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([task.to_dict() for task in self.tasks], f, 
                         ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存待办事项失败: {e}")
    
    def add_task(self, task: TodoTask) -> str:
        """添加新任务"""
        self.tasks.append(task)
        self.save_tasks()
        return task.task_id
    
    def get_task(self, task_id: str) -> Optional[TodoTask]:
        """根据ID获取任务"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """更新任务"""
        task = self.get_task(task_id)
        if task:
            task.update(**kwargs)
            self.save_tasks()
            return True
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            return True
        return False
    
    def mark_task_completed(self, task_id: str) -> bool:
        """标记任务为完成"""
        task = self.get_task(task_id)
        if task:
            task.mark_completed()
            self.save_tasks()
            return True
        return False
    
    def get_all_tasks(self, include_completed: bool = True) -> List[TodoTask]:
        """获取所有任务"""
        if include_completed:
            return self.tasks
        return [task for task in self.tasks if task.status != TaskStatus.COMPLETED]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[TodoTask]:
        """根据状态获取任务"""
        return [task for task in self.tasks if task.status == status]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[TodoTask]:
        """根据优先级获取任务"""
        return [task for task in self.tasks if task.priority == priority]
    
    def get_tasks_by_category(self, category: TaskCategory) -> List[TodoTask]:
        """根据分类获取任务"""
        return [task for task in self.tasks if task.category == category]
    
    def search_tasks(self, query: str) -> List[TodoTask]:
        """搜索任务"""
        query = query.lower()
        results = []
        for task in self.tasks:
            if (query in task.title.lower() or 
                query in task.description.lower() or
                any(query in tag.lower() for tag in task.tags)):
                results.append(task)
        return results
    
    def get_overdue_tasks(self) -> List[TodoTask]:
        """获取逾期任务"""
        return [task for task in self.tasks if task.is_overdue()]
    
    def get_tasks_due_today(self) -> List[TodoTask]:
        """获取今天到期的任务"""
        today = date.today().isoformat()
        return [task for task in self.tasks if task.due_date == today]
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        total = len(self.tasks)
        completed = len(self.get_tasks_by_status(TaskStatus.COMPLETED))
        pending = len(self.get_tasks_by_status(TaskStatus.PENDING))
        overdue = len(self.get_overdue_tasks())
        
        priority_counts = {}
        for priority in TaskPriority:
            priority_counts[priority.value] = len(self.get_tasks_by_priority(priority))
        
        category_counts = {}
        for category in TaskCategory:
            category_counts[category.value] = len(self.get_tasks_by_category(category))
        
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "overdue_tasks": overdue,
            "completion_rate": round(completed / total * 100, 2) if total > 0 else 0,
            "priority_distribution": priority_counts,
            "category_distribution": category_counts
        }
    
    def clear_completed_tasks(self):
        """清空已完成的任务"""
        self.tasks = [task for task in self.tasks if task.status != TaskStatus.COMPLETED]
        self.save_tasks()
    
    def export_tasks(self, filename: str = None) -> str:
        """导出任务到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"todo_export_{timestamp}.json"
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "total_tasks": len(self.tasks),
            "tasks": [task.to_dict() for task in self.tasks],
            "statistics": self.get_task_statistics()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return filename 