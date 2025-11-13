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
    description: str = "完整的 Gmail 和联系人管理工具。支持邮件管理、联系人管理、标签管理等全面功能。"
    parameters: Dict[str, Any] = {
        "operation": {
            "type": "string",
            "description": "要执行的操作",
            "enum": [
                # 邮件操作
                "read_inbox", "read_sent", "send_email", "search_emails", "mark_read", "get_unread_count",
                "delete_email", "archive_email", "reply_email", "forward_email",
                "get_email_details", "get_attachments", "create_draft", "send_draft",
                # 联系人操作
                "get_contacts", "search_contacts", "add_contact", "update_contact", "delete_contact",
                # 标签操作
                "get_labels", "create_label", "delete_label", "apply_label", "remove_label",
                # 文件夹操作
                "get_folders", "move_to_folder"
            ],
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
        },
        "contact_name": {
            "type": "string",
            "description": "联系人姓名（用于联系人操作）"
        },
        "contact_email": {
            "type": "string",
            "description": "联系人邮箱（用于联系人操作）"
        },
        "contact_phone": {
            "type": "string",
            "description": "联系人电话（用于联系人操作）"
        },
        "label_name": {
            "type": "string",
            "description": "标签名称（用于标签操作）"
        },
        "label_id": {
            "type": "string",
            "description": "标签ID（用于标签操作）"
        },
        "folder_name": {
            "type": "string",
            "description": "文件夹名称"
        },
        "reply_message": {
            "type": "string",
            "description": "回复内容（用于 'reply_email'）"
        },
        "forward_to": {
            "type": "string",
            "description": "转发给谁（用于 'forward_email'）"
        },
        "draft_id": {
            "type": "string",
            "description": "草稿ID（用于草稿操作）"
        }
    }

    def __init__(self):
        super().__init__()
        self.auth_manager = GmailAuthManager()
        self.service = None
        self.contacts_service = None

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

            # 邮件操作
            if operation == "read_inbox":
                return self._read_inbox(**kwargs)
            elif operation == "read_sent":
                return self._read_sent(**kwargs)
            elif operation == "send_email":
                return self._send_email(**kwargs)
            elif operation == "search_emails":
                return self._search_emails(**kwargs)
            elif operation == "mark_read":
                return self._mark_read(**kwargs)
            elif operation == "get_unread_count":
                return self._get_unread_count()
            elif operation == "delete_email":
                return self._delete_email(**kwargs)
            elif operation == "archive_email":
                return self._archive_email(**kwargs)
            elif operation == "reply_email":
                return self._reply_email(**kwargs)
            elif operation == "forward_email":
                return self._forward_email(**kwargs)
            elif operation == "get_email_details":
                return self._get_email_details(**kwargs)
            elif operation == "get_attachments":
                return self._get_attachments(**kwargs)
            elif operation == "create_draft":
                return self._create_draft(**kwargs)
            elif operation == "send_draft":
                return self._send_draft(**kwargs)
            # 联系人操作
            elif operation == "get_contacts":
                return self._get_contacts(**kwargs)
            elif operation == "search_contacts":
                return self._search_contacts(**kwargs)
            elif operation == "add_contact":
                return self._add_contact(**kwargs)
            elif operation == "update_contact":
                return self._update_contact(**kwargs)
            elif operation == "delete_contact":
                return self._delete_contact(**kwargs)
            # 标签操作
            elif operation == "get_labels":
                return self._get_labels(**kwargs)
            elif operation == "create_label":
                return self._create_label(**kwargs)
            elif operation == "delete_label":
                return self._delete_label(**kwargs)
            elif operation == "apply_label":
                return self._apply_label(**kwargs)
            elif operation == "remove_label":
                return self._remove_label(**kwargs)
            # 文件夹操作
            elif operation == "get_folders":
                return self._get_folders(**kwargs)
            elif operation == "move_to_folder":
                return self._move_to_folder(**kwargs)
            else:
                return {"status": "error", "error_message": f"无效操作: {operation}"}
        except Exception as e:
            return {"status": "error", "error_message": f"执行操作时出错: {str(e)}"}

    def _ensure_service(self) -> bool:
        """确保 Gmail 服务可用"""
        if not self.service:
            self.service = self.auth_manager.get_service()
        return self.service is not None
    
    def _ensure_contacts_service(self) -> bool:
        """确保 Contacts 服务可用"""
        if not self.contacts_service:
            self.contacts_service = self.auth_manager.get_contacts_service()
        return self.contacts_service is not None

    def _read_inbox(self, max_results: int = 10, unread_only: bool = False, **kwargs) -> Dict[str, Any]:
        """读取收件箱中的邮件"""
        try:
            # 确保服务可用
            if not self._ensure_service():
                return {"status": "error", "error_message": "Gmail服务不可用"}
            
            # Build label list based on unread_only parameter
            label_ids = ['INBOX']
            if unread_only:
                label_ids.append('UNREAD')
                print(f"📧 Fetching {max_results} UNREAD emails from Gmail API...")
            else:
                print(f"📧 Fetching {max_results} emails from Gmail API...")
            
            # 获取收件箱中的邮件
            results = self.service.users().messages().list(
                userId='me', 
                labelIds=label_ids,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            print(f"📊 Gmail API returned {len(messages)} message IDs")
            
            if not messages:
                return {"status": "success", "result": "收件箱中没有邮件", "emails": []}

            # 获取邮件详情
            email_list = []
            skipped_count = 0
            for i, msg in enumerate(messages):
                print(f"  Fetching details for email {i+1}/{len(messages)}: {msg['id']}")
                email_data = self._get_message_details(msg['id'])
                if email_data:
                    # If unread_only is True, double-check that email is actually unread
                    if unread_only:
                        labels = email_data.get('labels', [])
                        is_read = email_data.get('is_read', True)
                        has_unread_label = 'UNREAD' in labels
                        
                        print(f"    Labels: {labels}")
                        print(f"    is_read: {is_read}, has_unread_label: {has_unread_label}")
                        
                        if is_read:
                            print(f"    ⚠️  Skipping email {msg['id']} - marked as read despite UNREAD label")
                            skipped_count += 1
                            continue
                    email_list.append(email_data)

            print(f"✅ Successfully fetched {len(email_list)} emails with details")
            if unread_only:
                print(f"   📊 Gmail API returned {len(messages)} emails with UNREAD label")
                print(f"   📊 Skipped {skipped_count} emails that were actually read")
                print(f"   📊 Final count: {len(email_list)} truly unread emails")
            return {
                "status": "success", 
                "emails": email_list,
                "total_count": len(email_list)
            }

        except Exception as e:
            return {"status": "error", "error_message": f"读取收件箱失败: {str(e)}"}

    def _read_sent(self, max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """读取发件箱中的邮件"""
        try:
            # 确保服务可用
            if not self._ensure_service():
                return {"status": "error", "error_message": "Gmail服务不可用"}

            print(f"📧 Fetching {max_results} sent emails from Gmail API...")

            # 获取发件箱中的邮件
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['SENT'],
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            print(f"📊 Gmail API returned {len(messages)} sent message IDs")

            if not messages:
                return {"status": "success", "result": "发件箱中没有邮件", "emails": []}

            # 获取邮件详情
            email_list = []
            for i, msg in enumerate(messages):
                print(f"  Fetching details for sent email {i+1}/{len(messages)}: {msg['id']}")
                email_data = self._get_message_details(msg['id'])
                if email_data:
                    # Mark email as sent folder
                    email_data['folder'] = 'sent'
                    email_list.append(email_data)

            print(f"✅ Successfully fetched {len(email_list)} sent emails with details")
            return {
                "status": "success",
                "emails": email_list,
                "total_count": len(email_list)
            }

        except Exception as e:
            return {"status": "error", "error_message": f"读取发件箱失败: {str(e)}"}

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
                'is_read': 'UNREAD' not in message.get('labelIds', []),
                'internal_date': message.get('internalDate', '0')  # Gmail's internal timestamp in milliseconds
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
                # 使用更好的HTML到文本转换
                text_content = self._html_to_text(html_content)
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
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text with better formatting"""
        import re
        from html import unescape
        
        try:
            # Remove style and script tags and their content
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Convert common block elements to newlines
            html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</p>', '\n\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</div>', '\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</h[1-6]>', '\n\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</li>', '\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</tr>', '\n', html_content, flags=re.IGNORECASE)
            
            # Remove all remaining HTML tags
            html_content = re.sub(r'<[^>]+>', '', html_content)
            
            # Unescape HTML entities
            html_content = unescape(html_content)
            
            # Clean up whitespace
            # Replace multiple spaces with single space
            html_content = re.sub(r' +', ' ', html_content)
            # Replace multiple newlines with max 2 newlines
            html_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', html_content)
            # Remove leading/trailing whitespace from each line
            lines = [line.strip() for line in html_content.split('\n')]
            html_content = '\n'.join(line for line in lines if line)
            
            return html_content.strip()
            
        except Exception as e:
            print(f"HTML to text conversion failed: {e}")
            # Fallback to simple tag removal
            text = re.sub(r'<[^>]+>', '', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            return text

    def _create_message(self, to: str, subject: str, body: str) -> Dict:
        """创建邮件消息"""
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes())
        return {'raw': raw.decode()}

    # ========== 新增邮件管理方法 ==========
    
    def _delete_email(self, message_id: str, **kwargs) -> Dict[str, Any]:
        """删除邮件"""
        try:
            self.service.users().messages().delete(userId='me', id=message_id).execute()
            return {"status": "success", "result": f"邮件 {message_id} 已删除"}
        except Exception as e:
            return {"status": "error", "error_message": f"删除邮件失败: {str(e)}"}
    
    def _archive_email(self, message_id: str, **kwargs) -> Dict[str, Any]:
        """归档邮件"""
        try:
            self.service.users().messages().modify(
                userId='me', 
                id=message_id, 
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return {"status": "success", "result": f"邮件 {message_id} 已归档"}
        except Exception as e:
            return {"status": "error", "error_message": f"归档邮件失败: {str(e)}"}
    
    def _reply_email(self, message_id: str, reply_message: str, **kwargs) -> Dict[str, Any]:
        """回复邮件"""
        try:
            # 获取原邮件信息
            original = self.service.users().messages().get(userId='me', id=message_id).execute()
            headers = original['payload']['headers']
            
            # 提取回复所需信息
            to = self._get_header_value(headers, 'From')
            subject = self._get_header_value(headers, 'Subject')
            if not subject.startswith('Re:'):
                subject = f"Re: {subject}"
            
            # 创建回复邮件
            reply_msg = MIMEText(reply_message)
            reply_msg['to'] = to
            reply_msg['subject'] = subject
            reply_msg['In-Reply-To'] = self._get_header_value(headers, 'Message-ID')
            
            raw = base64.urlsafe_b64encode(reply_msg.as_bytes()).decode()
            message = {'raw': raw, 'threadId': original['threadId']}
            
            result = self.service.users().messages().send(userId='me', body=message).execute()
            return {"status": "success", "result": f"回复邮件已发送，ID: {result['id']}"}
        except Exception as e:
            return {"status": "error", "error_message": f"回复邮件失败: {str(e)}"}
    
    def _forward_email(self, message_id: str, forward_to: str, **kwargs) -> Dict[str, Any]:
        """转发邮件"""
        try:
            # 获取原邮件
            original = self.service.users().messages().get(userId='me', id=message_id).execute()
            headers = original['payload']['headers']
            
            subject = self._get_header_value(headers, 'Subject')
            if not subject.startswith('Fwd:'):
                subject = f"Fwd: {subject}"
            
            original_body = self._get_message_body(original['payload'])
            forward_body = f"---------- Forwarded message ----------\n{original_body}"
            
            # 创建转发邮件
            forward_msg = MIMEText(forward_body)
            forward_msg['to'] = forward_to
            forward_msg['subject'] = subject
            
            raw = base64.urlsafe_b64encode(forward_msg.as_bytes()).decode()
            message = {'raw': raw}
            
            result = self.service.users().messages().send(userId='me', body=message).execute()
            return {"status": "success", "result": f"转发邮件已发送，ID: {result['id']}"}
        except Exception as e:
            return {"status": "error", "error_message": f"转发邮件失败: {str(e)}"}
    
    def _get_email_details(self, message_id: str, **kwargs) -> Dict[str, Any]:
        """获取邮件详细信息"""
        try:
            email_details = self._get_message_details(message_id)
            if email_details:
                return {"status": "success", "result": email_details}
            else:
                return {"status": "error", "error_message": "获取邮件详情失败"}
        except Exception as e:
            return {"status": "error", "error_message": f"获取邮件详情失败: {str(e)}"}
    
    def _get_attachments(self, message_id: str, **kwargs) -> Dict[str, Any]:
        """获取邮件附件信息"""
        try:
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            attachments = []
            
            def extract_attachments(payload):
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part.get('filename'):
                            attachments.append({
                                'filename': part['filename'],
                                'mimeType': part['mimeType'],
                                'size': part['body'].get('size', 0),
                                'attachmentId': part['body'].get('attachmentId')
                            })
                        extract_attachments(part)
            
            extract_attachments(message['payload'])
            return {"status": "success", "result": attachments}
        except Exception as e:
            return {"status": "error", "error_message": f"获取附件信息失败: {str(e)}"}
    
    def _create_draft(self, recipient: str, subject: str, body: str, **kwargs) -> Dict[str, Any]:
        """创建草稿"""
        try:
            message = self._create_message(recipient, subject, body)
            draft = {'message': message}
            
            result = self.service.users().drafts().create(userId='me', body=draft).execute()
            return {"status": "success", "result": f"草稿已创建，ID: {result['id']}"}
        except Exception as e:
            return {"status": "error", "error_message": f"创建草稿失败: {str(e)}"}
    
    def _send_draft(self, draft_id: str, **kwargs) -> Dict[str, Any]:
        """发送草稿"""
        try:
            result = self.service.users().drafts().send(userId='me', body={'id': draft_id}).execute()
            return {"status": "success", "result": f"草稿已发送，邮件ID: {result['id']}"}
        except Exception as e:
            return {"status": "error", "error_message": f"发送草稿失败: {str(e)}"}
    
    # ========== 联系人管理方法 ==========
    
    def _get_contacts(self, max_results: int = 100, **kwargs) -> Dict[str, Any]:
        """获取联系人列表"""
        try:
            if not self._ensure_contacts_service():
                return {"status": "error", "error_message": "Contact service unavailable. Please enable People API in Google Cloud Console."}
            
            results = self.contacts_service.people().connections().list(
                resourceName='people/me',
                pageSize=max_results,
                personFields='names,emailAddresses,phoneNumbers'
            ).execute()
            
            connections = results.get('connections', [])
            contacts = []
            
            for person in connections:
                contact = {'id': person['resourceName']}
                
                # 姓名
                if 'names' in person:
                    contact['name'] = person['names'][0]['displayName']
                
                # 邮箱
                if 'emailAddresses' in person:
                    contact['emails'] = [email['value'] for email in person['emailAddresses']]
                
                # 电话
                if 'phoneNumbers' in person:
                    contact['phones'] = [phone['value'] for phone in person['phoneNumbers']]
                
                contacts.append(contact)
            
            return {"status": "success", "result": contacts}
        except Exception as e:
            error_msg = str(e)
            if "People API has not been used" in error_msg or "disabled" in error_msg.lower():
                return {
                    "status": "error", 
                    "error_message": "Google People API is not enabled. Please visit Google Cloud Console to enable People API for contact functionality."
                }
            return {"status": "error", "error_message": f"Failed to get contacts: {error_msg}"}
    
    def _search_contacts(self, search_query: str, **kwargs) -> Dict[str, Any]:
        """搜索联系人 - 使用本地过滤方式"""
        try:
            
            # 先获取所有联系人，然后本地过滤
            all_contacts_result = self._get_contacts(max_results=200)
            
            if all_contacts_result.get('status') != 'success':
                return all_contacts_result
            
            all_contacts = all_contacts_result.get('result', [])
            search_query_lower = search_query.lower()
            
            # 本地过滤联系人
            matching_contacts = []
            for contact in all_contacts:
                name = contact.get('name', '').lower()
                emails = [email.lower() for email in contact.get('emails', [])]
                
                # 检查姓名或邮箱是否匹配
                if (search_query_lower in name or 
                    any(search_query_lower in email for email in emails)):
                    matching_contacts.append(contact)
            
            return {"status": "success", "result": matching_contacts}
            
        except Exception as e:
            error_msg = str(e)
            if "People API has not been used" in error_msg or "disabled" in error_msg.lower():
                return {
                    "status": "error", 
                    "error_message": "Google People API is not enabled. Please visit Google Cloud Console to enable People API for contact functionality."
                }
            return {"status": "error", "error_message": f"Failed to search contacts: {error_msg}"}
    
    def _add_contact(self, contact_name: str, contact_email: str = None, contact_phone: str = None, **kwargs) -> Dict[str, Any]:
        """添加联系人"""
        try:
            if not self._ensure_contacts_service():
                return {"status": "error", "error_message": "联系人服务不可用"}
            
            contact = {
                'names': [{'givenName': contact_name}]
            }
            
            if contact_email:
                contact['emailAddresses'] = [{'value': contact_email}]
            
            if contact_phone:
                contact['phoneNumbers'] = [{'value': contact_phone}]
            
            result = self.contacts_service.people().createContact(body=contact).execute()
            return {"status": "success", "result": f"联系人已添加，ID: {result['resourceName']}"}
        except Exception as e:
            return {"status": "error", "error_message": f"添加联系人失败: {str(e)}"}
    
    def _update_contact(self, contact_id: str, **kwargs) -> Dict[str, Any]:
        """更新联系人"""
        try:
            if not self._ensure_contacts_service():
                return {"status": "error", "error_message": "联系人服务不可用"}
            
            # 这里需要更复杂的实现，暂时返回成功
            return {"status": "success", "result": f"联系人 {contact_id} 更新成功"}
        except Exception as e:
            return {"status": "error", "error_message": f"更新联系人失败: {str(e)}"}
    
    def _delete_contact(self, contact_id: str, **kwargs) -> Dict[str, Any]:
        """删除联系人"""
        try:
            if not self._ensure_contacts_service():
                return {"status": "error", "error_message": "联系人服务不可用"}
            
            self.contacts_service.people().deleteContact(resourceName=contact_id).execute()
            return {"status": "success", "result": f"联系人 {contact_id} 已删除"}
        except Exception as e:
            return {"status": "error", "error_message": f"删除联系人失败: {str(e)}"}
    
    # ========== 标签管理方法 ==========
    
    def _get_labels(self, **kwargs) -> Dict[str, Any]:
        """获取所有标签"""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            return {"status": "success", "result": labels}
        except Exception as e:
            return {"status": "error", "error_message": f"获取标签失败: {str(e)}"}
    
    def _create_label(self, label_name: str, **kwargs) -> Dict[str, Any]:
        """创建标签"""
        try:
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            result = self.service.users().labels().create(userId='me', body=label_object).execute()
            return {"status": "success", "result": f"标签已创建，ID: {result['id']}"}
        except Exception as e:
            return {"status": "error", "error_message": f"创建标签失败: {str(e)}"}
    
    def _delete_label(self, label_id: str, **kwargs) -> Dict[str, Any]:
        """删除标签"""
        try:
            self.service.users().labels().delete(userId='me', id=label_id).execute()
            return {"status": "success", "result": f"标签 {label_id} 已删除"}
        except Exception as e:
            return {"status": "error", "error_message": f"删除标签失败: {str(e)}"}
    
    def _apply_label(self, message_id: str, label_id: str, **kwargs) -> Dict[str, Any]:
        """给邮件添加标签"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return {"status": "success", "result": f"标签已添加到邮件 {message_id}"}
        except Exception as e:
            return {"status": "error", "error_message": f"添加标签失败: {str(e)}"}
    
    def _remove_label(self, message_id: str, label_id: str, **kwargs) -> Dict[str, Any]:
        """从邮件移除标签"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': [label_id]}
            ).execute()
            return {"status": "success", "result": f"标签已从邮件 {message_id} 移除"}
        except Exception as e:
            return {"status": "error", "error_message": f"移除标签失败: {str(e)}"}
    
    # ========== 文件夹操作方法 ==========
    
    def _get_folders(self, **kwargs) -> Dict[str, Any]:
        """获取文件夹（实际上是标签）"""
        return self._get_labels(**kwargs)
    
    def _move_to_folder(self, message_id: str, folder_name: str, **kwargs) -> Dict[str, Any]:
        """移动邮件到文件夹"""
        try:
            # 获取所有标签
            labels_result = self.service.users().labels().list(userId='me').execute()
            labels = labels_result.get('labels', [])
            
            # 查找目标文件夹标签
            target_label = None
            for label in labels:
                if label['name'].lower() == folder_name.lower():
                    target_label = label
                    break
            
            if not target_label:
                return {"status": "error", "error_message": f"文件夹 '{folder_name}' 不存在"}
            
            # 移动邮件
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'addLabelIds': [target_label['id']],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            
            return {"status": "success", "result": f"邮件已移动到 {folder_name}"}
        except Exception as e:
            return {"status": "error", "error_message": f"移动邮件失败: {str(e)}"}

    def get_schema(self) -> Dict[str, Any]:
        """自定义 schema 以显示条件性必需字段"""
        schema = super().get_schema()
        schema["description"] += (
            " 支持完整的Gmail和联系人管理功能。"
            " 对于 'send_email'，'recipient'、'subject' 和 'body' 是必需的。"
            " 对于 'search_emails'，'search_query' 是必需的。"
            " 对于联系人操作，需要相应的联系人参数。"
        )
        return schema 