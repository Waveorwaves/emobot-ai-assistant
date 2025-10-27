# Agent 意图理解改进

## 改进概述

将基于关键词匹配的意图识别系统重构为真正的 LLM Agent 系统，让模型自主理解用户意图并选择合适的工具。

## 主要变更

### 1. 移除强制性关键词检测

**之前的问题：**
- 使用大量 regex 模式匹配来检测用户意图
- 使用 `_check_requires_tool_execution()` 强制判断是否需要工具
- 使用 `_generate_tool_call_from_context()` 在模型未生成工具调用时强制生成

**改进后：**
- 完全依赖 LLM 模型理解用户意图
- 模型根据 system prompt 和上下文自主决定是否使用工具
- 只提取模型生成的 JSON 格式工具调用，不再强制生成

### 2. 改进 System Prompt

**新增内容：**

```markdown
**Natural Language Understanding:**
- Users may phrase requests in many different ways
- "I need u to list my contacts" = "get my contact list" = "show me my contacts"
- Focus on the ACTION the user wants (list, send, search, create, delete, etc.)
- Focus on the OBJECT of that action (contacts, emails, events, tasks, etc.)
- Then select the appropriate tool and operation

**Intent Understanding Examples:**
- "get my contact list" / "list my contacts" → email tool with operation="get_contacts"
- "what's Jason's email" → email tool with operation="search_contacts", search_query="Jason"
- "send email to jason@example.com" → email tool with operation="send_email"
- "check my calendar" / "what's on my schedule" → calendar tool with operation="list_events"
```

### 3. 改进 Thought Prompt

**新增工具列表展示：**
- 在每个推理步骤中展示可用工具
- 帮助模型了解有哪些工具可用

**新增意图理解指导：**
```
**Thought**: 
1. Understand what the user wants to achieve (not just the keywords they used)
2. Determine if you need to use a tool or can provide a final answer
3. If using a tool, select the appropriate tool and operation based on the user's intent
4. Consider the conversation context and previous tool results

IMPORTANT REMINDERS:
- Understand user INTENT, not just keywords
- "get my contact list" means use email tool with operation="get_contacts"
- "what's Jason's email" means use email tool with operation="search_contacts"
- "check my calendar" means use calendar tool with operation="list_events"
```

### 4. 简化代码结构

**删除的函数：**
- `_check_requires_tool_execution()` - 不再强制判断是否需要工具
- 简化 `_extract_tool_call()` - 只提取 JSON，不再尝试推断

**保留的辅助函数：**
- `_generate_tool_call_from_context()` - 标记为向后兼容，但不主动使用
- `_extract_email_content()` 等 - 保留用于特殊情况

## 工作原理

### 之前的流程：
```
用户输入 → 关键词匹配 → 强制生成工具调用 → 执行 → 返回结果
```

### 改进后的流程：
```
用户输入 → LLM 理解意图 → LLM 决定工具调用 → 提取 JSON → 执行 → 返回结果
```

## 优势

1. **更自然的理解**：模型可以理解各种表达方式，不局限于预定义的关键词
2. **更灵活**：无需为每种新的表达方式添加 regex 模式
3. **更智能**：模型可以根据上下文理解隐含的意图
4. **更可维护**：代码更简洁，逻辑更清晰

## 测试建议

测试以下场景确保改进有效：

1. **联系人查询**：
   - "get my contact list"
   - "list my contacts"
   - "I need u to list my contacts"
   - "show me all my contacts"

2. **邮件发送**：
   - "send email to jason@example.com"
   - "email jason@example.com about the meeting"
   - "I want to send a message to jason@example.com"

3. **日历查询**：
   - "check my calendar"
   - "what's on my schedule"
   - "show me my events"
   - "do I have any meetings today"

4. **任务管理**：
   - "add a task to buy groceries"
   - "show my todo list"
   - "mark task as done"

## 注意事项

1. 模型的理解能力依赖于 system prompt 的质量
2. 需要确保 system prompt 中的示例足够清晰
3. 如果模型理解出现偏差，应该改进 prompt 而不是添加关键词匹配
4. 保持对话历史的上下文很重要，帮助模型理解连续的请求

## 未来改进方向

1. **Few-shot Learning**：在 prompt 中添加更多示例
2. **动态示例选择**：根据用户查询选择最相关的示例
3. **反馈学习**：收集用户反馈，改进模型理解
4. **工具描述优化**：为每个工具提供更详细的描述和使用场景
