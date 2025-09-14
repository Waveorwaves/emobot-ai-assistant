"""
真实的 Gmail 邮件管理工具
集成 Gmail API，提供完整的邮件管理功能
"""

from .tool_base import MCPToolBase
from .gmail_auth import GmailAuthManager
from typing import Dict, Any, List
import base64
import email
from email.mime.text import MIMEText
import re
from datetime import datetime, timezone
import json

class EmailTool(MCPToolBase):
    """
    真实的 Gmail 邮件管理工具
    支持读取收件箱、发送邮件、搜索邮件、标记已读等功能
    """
    
    name: str = "email"
    description: str = "管理 Gmail 邮件。支持读取收件箱、发送邮件、搜索邮件、标记已读等操作。"
    parameters: Dict[str, Any] = {
        "operation": {
            "type": "string",
            "description": "要执行的操作。可以是 'read_inbox', 'send_email', 'search_emails', 'mark_read', 'get_unread_count'",
            "enum": ["read_inbox", "send_email", "search_emails", "mark_read", "get_unread_count"],
        },
        "recipient": {
            "type": "string",
            "description": "收件人邮箱地址（用于 'send_email'）"
        },
        "subject": {
            "type": "string",
            "description": "邮件主题（用于 'send_email'）"
        },
        "body": {
            "type": "string",
            "description": "邮件内容（用于 'send_email'）"
        },
        "search_query": {
            "type": "string",
            "description": "搜索查询（用于 'search_emails'）"
        },
        "message_id": {
            "type": "string",
            "description": "邮件 ID（用于 'mark_read'）"
        },
        "max_results": {
            "type": "integer",
            "description": "最大结果数量（用于 'read_inbox' 和 'search_emails'）",
            "default": 10
        }
    }

    def __init__(self):
        super().__init__()
        self.auth_manager = GmailAuthManager()
        self.service = None

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行指定的邮件操作

        Args:
            **kwargs: 包含operation和其他参数的字典

        Returns:
            包含操作结果的字典
        """
        try:
            operation = kwargs.get("operation")
            if not operation:
                return {"status": "error", "error_message": "缺少operation参数"}

            # 确保 Gmail 服务可用
            if not self._ensure_service():
                return {"status": "error", "error_message": "Gmail 服务不可用，请检查认证配置"}

            if operation == "read_inbox":
                return self._read_inbox(**kwargs)
            elif operation == "send_email":
                return self._send_email(**kwargs)
            elif operation == "search_emails":
                return self._search_emails(**kwargs)
            elif operation == "mark_read":
                return self._mark_read(**kwargs)
            elif operation == "get_unread_count":
                return self._get_unread_count()
            else:
                return {"status": "error", "error_message": f"无效操作: {operation}"}
        except Exception as e:
            return {"status": "error", "error_message": f"执行操作时出错: {str(e)}"}

    def _ensure_service(self) -> bool:
        """确保 Gmail 服务可用"""
        if not self.service:
            self.service = self.auth_manager.get_service()
        return self.service is not None

    def _read_inbox(self, max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """读取收件箱中的邮件"""
        try:
            # 确保服务可用
            if not self._ensure_service():
                return {"status": "error", "error_message": "Gmail服务不可用"}
            
            # 获取收件箱中的邮件
            results = self.service.users().messages().list(
                userId='me', 
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                return {"status": "success", "result": "收件箱中没有邮件"}

            # 获取邮件详情
            email_list = []
            for msg in messages:
                email_data = self._get_message_details(msg['id'])
                if email_data:
                    email_list.append(email_data)

            return {
                "status": "success", 
                "emails": email_list,
                "total_count": len(email_list)
            }

        except Exception as e:
            return {"status": "error", "error_message": f"读取收件箱失败: {str(e)}"}

    def _send_email(self, recipient: str, subject: str, body: str, **kwargs) -> Dict[str, Any]:
        """发送邮件"""
        try:
            if not all([recipient, subject, body]):
                return {"status": "error", "error_message": "收件人、主题和内容都是必需的"}

            # 确保服务可用
            if not self._ensure_service():
                return {"status": "error", "error_message": "Gmail服务不可用"}

            # 构建邮件
            message = self._create_message(recipient, subject, body)
            
            # 发送邮件
            sent_message = self.service.users().messages().send(
                userId='me', 
                body=message
            ).execute()

            return {
                "status": "success", 
                "result": f"Email successfully sent to {recipient}",
                "message_id": sent_message['id']
            }

        except Exception as e:
            return {"status": "error", "error_message": f"发送邮件失败: {str(e)}"}

    def _search_emails(self, search_query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """搜索邮件"""
        try:
            if not search_query:
                return {"status": "error", "error_message": "搜索查询不能为空"}

            # 执行搜索
            results = self.service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                return {"status": "success", "result": f"No emails found matching '{search_query}' 的邮件"}

            # 获取邮件详情
            email_list = []
            for msg in messages:
                email_data = self._get_message_details(msg['id'])
                if email_data:
                    email_list.append(email_data)

            return {
                "status": "success", 
                "emails": email_list,
                "total_count": len(email_list)
            }

        except Exception as e:
            return {"status": "error", "error_message": f"搜索邮件失败: {str(e)}"}

    def _mark_read(self, message_id: str, **kwargs) -> Dict[str, Any]:
        """标记邮件为已读"""
        try:
            if not message_id:
                return {"status": "error", "error_message": "邮件 ID 不能为空"}

            # 移除 UNREAD 标签
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            return {"status": "success", "result": "Email marked as read"}

        except Exception as e:
            return {"status": "error", "error_message": f"Mark email failed: {str(e)}"}

    def _get_unread_count(self) -> Dict[str, Any]:
        """获取未读邮件数量"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['UNREAD'],
                maxResults=1
            ).execute()

            total_count = results.get('resultSizeEstimate', 0)
            return {
                "status": "success", 
                "unread_count": total_count
            }

        except Exception as e:
            return {"status": "error", "error_message": f"Get unread count failed: {str(e)}"}

    def _get_message_details(self, message_id: str) -> Dict[str, Any]:
        """获取邮件详细信息"""
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            
            # 提取邮件信息
            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'subject': self._get_header_value(headers, 'Subject'),
                'from': self._get_header_value(headers, 'From'),
                'to': self._get_header_value(headers, 'To'),
                'date': self._get_header_value(headers, 'Date'),
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', []),
                'is_read': 'UNREAD' not in message.get('labelIds', [])
            }

            # 获取邮件内容
            body = self._get_message_body(message['payload'])
            if body:
                email_data['body'] = body

            return email_data

        except Exception as e:
            print(f"获取邮件详情失败: {e}")
            return None

    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        """从邮件头中获取指定值"""
        for header in headers:
            if header['name'] == name:
                return header['value']
        return ''

    def _get_message_body(self, payload: Dict) -> str:
        """获取邮件正文内容"""
        try:
            # 首先尝试获取纯文本内容
            text_content = self._extract_text_content(payload)
            if text_content:
                return text_content
            
            # 如果没有纯文本，尝试获取HTML内容
            html_content = self._extract_html_content(payload)
            if html_content:
                # 简单的HTML到文本转换
                import re
                # 移除HTML标签
                text_content = re.sub(r'<[^>]+>', '', html_content)
                # 移除多余的空白字符
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                return text_content
            
            return ''
        except Exception as e:
            print(f"解析邮件正文失败: {e}")
            return ''
    
    def _extract_text_content(self, payload: Dict) -> str:
        """提取纯文本内容"""
        try:
            if 'body' in payload and payload['body'].get('data'):
                data = payload['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8')
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if part['body'].get('data'):
                            data = part['body']['data']
                            return base64.urlsafe_b64decode(data).decode('utf-8')
                    elif part['mimeType'] == 'multipart/alternative':
                        # 递归处理多部分内容
                        text_content = self._extract_text_content(part)
                        if text_content:
                            return text_content
            
            return ''
        except Exception as e:
            print(f"提取文本内容失败: {e}")
            return ''
    
    def _extract_html_content(self, payload: Dict) -> str:
        """提取HTML内容"""
        try:
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/html':
                        if part['body'].get('data'):
                            data = part['body']['data']
                            return base64.urlsafe_b64decode(data).decode('utf-8')
                    elif part['mimeType'] == 'multipart/alternative':
                        # 递归处理多部分内容
                        html_content = self._extract_html_content(part)
                        if html_content:
                            return html_content
            
            return ''
        except Exception as e:
            print(f"提取HTML内容失败: {e}")
            return ''

    def _create_message(self, to: str, subject: str, body: str) -> Dict:
        """创建邮件消息"""
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes())
        return {'raw': raw.decode()}

    def get_schema(self) -> Dict[str, Any]:
        """自定义 schema 以显示条件性必需字段"""
        schema = super().get_schema()
        schema["description"] += (
            " 对于 'send_email'，'recipient'、'subject' 和 'body' 是必需的。"
            " 对于 'search_emails'，'search_query' 是必需的。"
            " 对于 'mark_read'，'message_id' 是必需的。"
        )
        return schema 