"""
Gmail API 认证管理器
处理 OAuth 2.0 认证流程和 token 管理
"""

import os
import json
import pickle
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import yaml

class GmailAuthManager:
    """Gmail API 认证管理器"""
    
    def __init__(self, config_path: str = "configs/gmail_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.credentials = None
        self.service = None
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)['gmail']
        except Exception as e:
            print(f"❌ 加载 Gmail 配置失败: {e}")
            return {}
    
    def authenticate(self) -> bool:
        """执行 Gmail 认证流程"""
        try:
            # 检查是否有有效的 token
            if self._load_existing_token():
                return True
            
            # 如果没有 token，执行 OAuth 流程
            if self._perform_oauth_flow():
                return True
                
        except Exception as e:
            print(f"❌ Gmail 认证失败: {e}")
            
        return False
    
    def _load_existing_token(self) -> bool:
        """加载现有的认证 token"""
        token_file = self.config.get('token_file', 'gmail_token.json')
        
        if not os.path.exists(token_file):
            return False
            
        try:
            with open(token_file, 'r') as token:
                token_data = json.load(token)
                
            self.credentials = Credentials.from_authorized_user_info(
                token_data, 
                self.config['scopes']
            )
            
            # 检查 token 是否过期
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                self._save_token()
                
            return True
            
        except Exception as e:
            print(f"❌ 加载 token 失败: {e}")
            return False
    
    def _perform_oauth_flow(self) -> bool:
        """执行 OAuth 2.0 认证流程"""
        try:
            # 创建 OAuth 流程
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": self.config['client_id'],
                        "client_secret": self.config['client_secret'],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.config['redirect_uri']]
                    }
                },
                self.config['scopes']
            )
            
            # 启动本地服务器进行认证，使用不同的端口避免冲突
            self.credentials = flow.run_local_server(
                port=8082,  # 使用 8082 端口避免与其他服务冲突
                open_browser=True
            )
            
            # 保存 token
            self._save_token()
            return True
            
        except Exception as e:
            print(f"❌ OAuth 流程失败: {e}")
            return False
    
    def _save_token(self):
        """保存认证 token"""
        if not self.credentials:
            return
            
        token_file = self.config.get('token_file', 'gmail_token.json')
        
        token_data = {
            'token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token,
            'token_uri': self.credentials.token_uri,
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
            'scopes': self.credentials.scopes
        }
        
        with open(token_file, 'w') as token:
            json.dump(token_data, token)
        
        print(f"✅ Token saved to {token_file}")
    
    def get_service(self):
        """获取 Gmail 服务实例"""
        if not self.credentials:
            if not self.authenticate():
                return None
                
        if not self.service:
            try:
                self.service = build('gmail', 'v1', credentials=self.credentials)
                print("✅ Gmail service connected successfully")
            except Exception as e:
                print(f"❌ Failed to create Gmail service: {e}")
                return None
                
        return self.service
    
    def test_connection(self) -> bool:
        """测试 Gmail 连接"""
        try:
            service = self.get_service()
            if not service:
                return False
                
            # 获取用户信息
            profile = service.users().getProfile(userId='me').execute()
            email = profile['emailAddress']
            print(f"✅ 成功连接到 Gmail: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Gmail 连接测试失败: {e}")
            return False 