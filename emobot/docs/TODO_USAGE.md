# 待办事项功能使用说明

## 🎯 **功能概述**

Emobot 的待办事项功能提供了完整的任务管理能力，包括：

- ✅ **任务创建和管理**
- 📊 **优先级和分类系统**
- 🔍 **搜索和过滤功能**
- 📅 **截止日期管理**
- 📈 **统计和分析**
- 💾 **数据持久化存储**

## 🚀 **快速开始**

### **1. 添加任务**

```python
# 基本任务
{
    "operation": "add_task",
    "title": "完成项目报告",
    "description": "编写季度项目总结报告",
    "priority": "high",
    "category": "work"
}

# 带截止日期的任务
{
    "operation": "add_task",
    "title": "购买生日礼物",
    "description": "为朋友准备生日礼物",
    "priority": "medium",
    "category": "personal",
    "due_date": "2025-08-15",
    "tags": ["礼物", "生日", "朋友"]
}
```

### **2. 查看任务列表**

```python
# 查看所有任务（包括已完成的）
{
    "operation": "view_list",
    "include_completed": true
}

# 只查看未完成的任务
{
    "operation": "view_list",
    "include_completed": false
}
```

### **3. 管理任务**

```python
# 查看特定任务详情
{
    "operation": "view_task",
    "task_id": "task_uuid_here"
}

# 更新任务
{
    "operation": "update_task",
    "task_id": "task_uuid_here",
    "description": "更新后的描述",
    "priority": "urgent"
}

# 标记任务完成
{
    "operation": "mark_done",
    "task_id": "task_uuid_here"
}

# 删除任务
{
    "operation": "delete_task",
    "task_id": "task_uuid_here"
}
```

## 🔧 **支持的操作**

| 操作 | 描述 | 必需参数 |
|------|------|----------|
| `add_task` | 添加新任务 | `title` |
| `view_list` | 查看任务列表 | 无 |
| `view_task` | 查看特定任务 | `task_id` |
| `update_task` | 更新任务 | `task_id` + 要更新的字段 |
| `delete_task` | 删除任务 | `task_id` |
| `mark_done` | 标记任务完成 | `task_id` |
| `search_tasks` | 搜索任务 | `query` |
| `get_statistics` | 获取统计信息 | 无 |
| `get_overdue` | 获取逾期任务 | 无 |
| `get_due_today` | 获取今天到期的任务 | 无 |
| `clear_completed` | 清空已完成的任务 | 无 |
| `export_tasks` | 导出任务数据 | 无 |

## 📊 **任务属性**

### **优先级 (Priority)**
- `low` - 低优先级
- `medium` - 中等优先级（默认）
- `high` - 高优先级
- `urgent` - 紧急优先级

### **分类 (Category)**
- `work` - 工作
- `personal` - 个人
- `study` - 学习
- `health` - 健康
- `shopping` - 购物
- `other` - 其他

### **状态 (Status)**
- `pending` - 待处理（默认）
- `in_progress` - 进行中
- `completed` - 已完成
- `cancelled` - 已取消

## 🔍 **高级功能**

### **搜索任务**
```python
{
    "operation": "search_tasks",
    "query": "Python"
}
```
搜索会在任务标题、描述和标签中查找匹配内容。

### **获取统计信息**
```python
{
    "operation": "get_statistics"
}
```
返回任务的统计信息，包括：
- 总任务数
- 已完成任务数
- 待处理任务数
- 逾期任务数
- 完成率
- 优先级分布
- 分类分布

### **获取逾期任务**
```python
{
    "operation": "get_overdue"
}
```
返回所有已过截止日期但未完成的任务。

### **获取今天到期的任务**
```python
{
    "operation": "get_due_today"
}
```
返回今天到期的任务列表。

### **导出任务数据**
```python
{
    "operation": "export_tasks"
}
```
将所有任务导出为 JSON 文件，包含完整的任务信息和统计。

## 💾 **数据存储**

- **存储文件**: `todo_list.json`
- **格式**: JSON
- **位置**: 项目根目录
- **自动保存**: 每次操作后自动保存
- **备份**: 支持导出功能

## 🧪 **测试功能**

运行测试脚本验证所有功能：

```bash
python test_todo.py
```

测试包括：
- 数据模型测试
- 任务管理器测试
- 工具接口测试
- 所有操作的功能验证

## 📝 **使用示例**

### **工作流程示例**

1. **创建任务**
   ```python
   # 添加工作任务
   {
       "operation": "add_task",
       "title": "准备会议材料",
       "description": "整理明天的团队会议所需材料",
       "priority": "high",
       "category": "work",
       "due_date": "2025-08-11"
   }
   ```

2. **查看任务**
   ```python
   # 查看所有任务
   {
       "operation": "view_list"
   }
   ```

3. **更新任务**
   ```python
   # 更新任务描述
   {
       "operation": "update_task",
       "task_id": "task_uuid",
       "description": "整理明天的团队会议所需材料，包括项目进度报告"
   }
   ```

4. **完成任务**
   ```python
   # 标记任务完成
   {
       "operation": "mark_done",
       "task_id": "task_uuid"
   }
   ```

5. **查看统计**
   ```python
   # 查看完成情况
   {
       "operation": "get_statistics"
   }
   ```

## 🚨 **注意事项**

1. **任务ID**: 每个任务都有唯一的UUID，操作时需要提供正确的ID
2. **日期格式**: 截止日期使用 `YYYY-MM-DD` 格式
3. **数据持久化**: 所有操作都会自动保存到文件
4. **错误处理**: 工具会返回详细的错误信息
5. **性能**: 支持大量任务，但建议定期清理已完成的任务

## 🔧 **故障排除**

### **常见问题**

1. **任务ID不存在**
   - 检查ID是否正确
   - 使用 `view_list` 查看所有任务

2. **文件权限错误**
   - 确保有写入权限
   - 检查磁盘空间

3. **数据损坏**
   - 使用 `export_tasks` 备份数据
   - 删除损坏的文件重新开始

### **获取帮助**

如果遇到问题，可以：
1. 查看错误信息
2. 运行测试脚本验证功能
3. 检查日志文件
4. 联系技术支持

---

🎉 **现在您可以开始使用强大的待办事项管理功能了！** 