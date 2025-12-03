#!/usr/bin/env python3
"""
待办事项管理工具
提供完整的任务管理功能
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from .todo_models import TodoListManager, TodoTask, TaskPriority, TaskStatus, TaskCategory
from .tool_base import MCPToolBase

class TodoListTool(MCPToolBase):
    """待办事项管理工具"""
    
    name = "todo_list"
    description = "管理待办事项列表，支持添加、查看、更新、删除、搜索等操作"
    
    def __init__(self):
        super().__init__()
        self.manager = TodoListManager()
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具模式"""
        return {
            "name": "todo_list",
            "description": "管理待办事项列表，支持添加、查看、更新、删除、搜索等操作",
            "parameters": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "add_task",
                        "view_list", 
                        "view_task",
                        "update_task",
                        "delete_task",
                        "mark_done",
                        "search_tasks",
                        "get_statistics",
                        "get_overdue",
                        "get_due_today",
                        "clear_completed",
                        "export_tasks"
                    ],
                    "description": "要执行的操作"
                },
                "task_id": {
                    "type": "string",
                    "description": "任务ID（用于查看、更新、删除、标记完成等操作）"
                },
                "title": {
                    "type": "string",
                    "description": "任务标题"
                },
                "task": {
                    "type": "string",
                    "description": "任务标题（title的别名）"
                },
                "description": {
                    "type": "string",
                    "description": "任务描述"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                    "description": "任务优先级"
                },
                "category": {
                    "type": "string",
                    "enum": ["work", "personal", "study", "health", "shopping", "other"],
                    "description": "任务分类"
                },
                "due_date": {
                    "type": "string",
                    "description": "截止日期（YYYY-MM-DD格式）"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "任务标签列表"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed", "cancelled"],
                    "description": "任务状态"
                },
                "query": {
                    "type": "string",
                    "description": "搜索查询（用于搜索操作）"
                },
                "include_completed": {
                    "type": "boolean",
                    "description": "是否包含已完成的任务（用于查看列表）"
                }
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行待办事项操作"""
        try:
            operation = kwargs.get("operation")
            
            if operation == "add_task":
                return self._add_task(kwargs)
            elif operation == "view_list":
                return self._view_list(kwargs)
            elif operation == "view_task":
                return self._view_task(kwargs)
            elif operation == "update_task":
                return self._update_task(kwargs)
            elif operation == "delete_task":
                return self._delete_task(kwargs)
            elif operation == "mark_done":
                return self._mark_done(kwargs)
            elif operation == "search_tasks":
                return self._search_tasks(kwargs)
            elif operation == "get_statistics":
                return self._get_statistics()
            elif operation == "get_overdue":
                return self._get_overdue_tasks()
            elif operation == "get_due_today":
                return self._get_due_today_tasks()
            elif operation == "clear_completed":
                return self._clear_completed_tasks()
            elif operation == "export_tasks":
                return self._export_tasks()
            else:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {operation}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时发生错误: {str(e)}"
            }
    
    def _add_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """添加新任务"""
        # 支持"title"和"task"两种字段名
        import logging
        logging.warning(f"DEBUG: _add_task called with parameters: {parameters}")
        print(f"📝 Adding task: {parameters}")
        title = parameters.get("title") or parameters.get("task")
        if not title:
            return {"status": "error", "message": "任务标题不能为空"}
        
        # Create task object
        try:
            category_str = str(parameters.get("category", "other")).lower().strip()
            category = TaskCategory(category_str)
        except ValueError:
            logging.warning(f"Invalid category: {parameters.get('category')}, defaulting to OTHER")
            category = TaskCategory.OTHER

        task = TodoTask(
            title=title,
            description=parameters.get("description", ""),
            priority=TaskPriority(parameters.get("priority", "medium")),
            category=category,
            due_date=parameters.get("due_date"),
            tags=parameters.get("tags", [])
        )
        
        # 保存任务
        task_id = self.manager.add_task(task)
        
        return {
            "status": "success",
            "message": "任务添加成功",
            "task_id": task_id,
            "task": task.to_dict()
        }
    
    def _view_list(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """查看任务列表"""
        include_completed = parameters.get("include_completed", True)
        tasks = self.manager.get_all_tasks(include_completed)
        
        # 按优先级和创建时间排序
        tasks.sort(key=lambda x: (-x.get_priority_score(), x.created_at))
        
        # 格式化任务列表
        formatted_tasks = []
        for task in tasks:
            formatted_task = {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "category": task.category.value,
                "due_date": task.due_date,
                "overdue": task.is_overdue(),
                "created_at": task.created_at
            }
            formatted_tasks.append(formatted_task)
        
        return {
            "status": "success",
            "total_tasks": len(formatted_tasks),
            "tasks": formatted_tasks
        }
    
    def _view_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """查看特定任务详情"""
        task_id = parameters.get("task_id")
        if not task_id:
            return {"status": "error", "message": "任务ID不能为空"}
        
        task = self.manager.get_task(task_id)
        if not task:
            return {"status": "error", "message": "任务不存在"}
        
        return {
            "status": "success",
            "task": task.to_dict()
        }
    
    def _update_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """更新任务"""
        task_id = parameters.get("task_id")
        if not task_id:
            return {"status": "error", "message": "任务ID不能为空"}
        
        # 准备更新数据
        update_data = {}
        if "title" in parameters:
            update_data["title"] = parameters["title"]
        if "description" in parameters:
            update_data["description"] = parameters["description"]
        if "priority" in parameters:
            update_data["priority"] = TaskPriority(parameters["priority"])
        if "category" in parameters:
            update_data["category"] = TaskCategory(parameters["category"])
        if "due_date" in parameters:
            update_data["due_date"] = parameters["due_date"]
        if "tags" in parameters:
            update_data["tags"] = parameters["tags"]
        if "status" in parameters:
            update_data["status"] = TaskStatus(parameters["status"])
        
        if not update_data:
            return {"status": "error", "message": "没有提供要更新的数据"}
        
        # 执行更新
        success = self.manager.update_task(task_id, **update_data)
        if success:
            task = self.manager.get_task(task_id)
            return {
                "status": "success",
                "message": "任务更新成功",
                "task": task.to_dict()
            }
        else:
            return {"status": "error", "message": "任务更新失败"}
    
    def _delete_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """删除任务"""
        task_id = parameters.get("task_id")
        if not task_id:
            return {"status": "error", "message": "任务ID不能为空"}
        
        success = self.manager.delete_task(task_id)
        if success:
            return {"status": "success", "message": "任务删除成功"}
        else:
            return {"status": "error", "message": "任务删除失败"}
    
    def _mark_done(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """标记任务为完成"""
        task_id = parameters.get("task_id")
        if not task_id:
            return {"status": "error", "message": "任务ID不能为空"}
        
        success = self.manager.mark_task_completed(task_id)
        if success:
            task = self.manager.get_task(task_id)
            return {
                "status": "success",
                "message": "任务标记为完成",
                "task": task.to_dict()
            }
        else:
            return {"status": "error", "message": "任务标记失败"}
    
    def _search_tasks(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """搜索任务"""
        query = parameters.get("query")
        if not query:
            return {"status": "error", "message": "搜索查询不能为空"}
        
        results = self.manager.search_tasks(query)
        formatted_results = [task.to_dict() for task in results]
        
        return {
            "status": "success",
            "query": query,
            "total_results": len(formatted_results),
            "results": formatted_results
        }
    
    def _get_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        stats = self.manager.get_task_statistics()
        return {
            "status": "success",
            "statistics": stats
        }
    
    def _get_overdue_tasks(self) -> Dict[str, Any]:
        """获取逾期任务"""
        overdue_tasks = self.manager.get_overdue_tasks()
        formatted_tasks = [task.to_dict() for task in overdue_tasks]
        
        return {
            "status": "success",
            "total_overdue": len(formatted_tasks),
            "overdue_tasks": formatted_tasks
        }
    
    def _get_due_today_tasks(self) -> Dict[str, Any]:
        """获取今天到期的任务"""
        due_today_tasks = self.manager.get_tasks_due_today()
        formatted_tasks = [task.to_dict() for task in due_today_tasks]
        
        return {
            "status": "success",
            "total_due_today": len(formatted_tasks),
            "due_today_tasks": formatted_tasks
        }
    
    def _clear_completed_tasks(self) -> Dict[str, Any]:
        """清空已完成的任务"""
        before_count = len(self.manager.get_tasks_by_status(TaskStatus.COMPLETED))
        self.manager.clear_completed_tasks()
        after_count = len(self.manager.get_tasks_by_status(TaskStatus.COMPLETED))
        
        return {
            "status": "success",
            "message": f"已清空 {before_count - after_count} 个已完成的任务"
        }
    
    def _export_tasks(self) -> Dict[str, Any]:
        """导出任务"""
        filename = self.manager.export_tasks()
        return {
            "status": "success",
            "message": "任务导出成功",
            "filename": filename
        } 