from typing import Dict, Any, List, Optional
import re
import json

class PerceptionModule:
    """
    感知模块：处理和理解用户输入
    
    负责接收用户输入并转换为结构化格式，包括：
    - 意图识别
    - 实体抽取
    - 输入类型分类
    - 情感分析（可扩展）
    """
    
    def __init__(self):
        # 定义意图关键词映射
        self.intent_keywords = {
            "search": ["搜索", "查找", "找", "search", "find", "查询"],
            "email": ["邮件", "邮箱", "发送邮件", "email", "mail", "发邮件"],
            "todo": ["待办", "任务", "todo", "task", "提醒", "事项"],
            "question": ["什么", "为什么", "怎么", "如何", "what", "why", "how"],
            "command": ["执行", "运行", "做", "创建", "删除", "修改"]
        }
        
        # 定义实体模式
        self.entity_patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "url": re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            "number": re.compile(r'\b\d+\b'),
            "quoted": re.compile(r'"([^"]*)"')
        }

    def process_input(self, raw_input: str) -> Dict[str, Any]:
        """
        处理用户输入，返回结构化数据
        
        Args:
            raw_input: 原始用户输入
            
        Returns:
            包含处理后信息的字典
        """
        if not isinstance(raw_input, str):
            return {
                "status": "error",
                "error_message": "输入必须是字符串",
                "original_input": raw_input
            }
        
        # 基础清理
        cleaned_text = raw_input.strip()
        
        # 识别意图
        intent = self._identify_intent(cleaned_text)
        
        # 抽取实体
        entities = self._extract_entities(cleaned_text)
        
        # 分析输入类型
        input_type = self._classify_input_type(cleaned_text)
        
        return {
            "status": "success",
            "type": input_type,
            "content": cleaned_text,
            "intent": intent,
            "entities": entities,
            "original_input": raw_input,
            "processed_at": self._get_timestamp()
        }
    
    def _identify_intent(self, text: str) -> Optional[str]:
        """识别用户意图"""
        text_lower = text.lower()
        
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return intent
        
        return "general"
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """从文本中抽取实体"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = pattern.findall(text)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def _classify_input_type(self, text: str) -> str:
        """分类输入类型"""
        # 检查是否是问题
        if any(text.strip().endswith(p) for p in ["?", "？"]):
            return "question"
        
        # 检查是否包含命令词
        command_words = ["请", "帮我", "需要", "想要", "执行"]
        if any(word in text for word in command_words):
            return "command"
        
        # 默认为查询
        return "query"
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def extract_task_context(self, processed_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        从处理后的输入中提取任务上下文
        
        Args:
            processed_input: process_input 的输出
            
        Returns:
            任务上下文信息
        """
        return {
            "task_type": processed_input.get("intent", "general"),
            "parameters": processed_input.get("entities", {}),
            "priority": self._estimate_priority(processed_input),
            "requires_tools": self._check_tool_requirement(processed_input)
        }
    
    def _estimate_priority(self, processed_input: Dict[str, Any]) -> str:
        """估计任务优先级"""
        content = processed_input.get("content", "").lower()
        
        # 高优先级关键词
        high_priority_words = ["紧急", "重要", "立即", "马上", "urgent", "important", "asap"]
        if any(word in content for word in high_priority_words):
            return "high"
        
        # 低优先级关键词
        low_priority_words = ["有空", "不急", "随便", "later", "whenever"]
        if any(word in content for word in low_priority_words):
            return "low"
        
        return "normal"
    
    def _check_tool_requirement(self, processed_input: Dict[str, Any]) -> bool:
        """检查是否需要调用工具"""
        intent = processed_input.get("intent", "")
        return intent in ["search", "email", "todo", "command"]