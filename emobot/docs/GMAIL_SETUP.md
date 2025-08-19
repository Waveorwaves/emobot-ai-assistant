# Gmail API 设置指南

本指南将帮助您设置 Gmail API 以使用 Emobot 的邮件功能。

## 步骤 1: 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 点击"创建项目"或选择现有项目
3. 为项目命名（例如："Emobot Gmail Integration"）
4. 点击"创建"

## 步骤 2: 启用 Gmail API

1. 在 Google Cloud Console 中，选择您的项目
2. 在左侧菜单中，点击"API 和服务" > "库"
3. 搜索 "Gmail API"
4. 点击 Gmail API，然后点击"启用"

## 步骤 3: 创建 OAuth 2.0 凭据

1. 在左侧菜单中，点击"API 和服务" > "凭据"
2. 点击"创建凭据" > "OAuth 客户端 ID"
3. 如果提示配置 OAuth 同意屏幕：
   - 选择"外部"用户类型
   - 填写应用名称（例如："Emobot"）
   - 填写用户支持电子邮件
   - 添加您的邮箱作为测试用户
4. 在"应用类型"中选择"桌面应用"
5. 为客户端命名（例如："Emobot Desktop Client"）
6. 点击"创建"

## 步骤 4: 下载凭据文件

1. 创建凭据后，点击"下载 JSON"
2. 将下载的文件重命名为 `gmail_credentials.json`
3. 将文件放在项目根目录下

## 步骤 5: 配置 Emobot

1. 编辑 `configs/gmail_config.yaml` 文件
2. 将您的 Gmail 邮箱地址填入 `user_email` 字段
3. **重要**: 确保 `redirect_uri` 设置为 `http://localhost:8081/oauth/callback` (使用 8081 端口避免与 Emobot 服务器冲突)

## 步骤 6: 首次认证

1. 启动 Emobot：`python main.py`
2. 首次使用邮件功能时，系统会自动打开浏览器
3. 登录您的 Google 账户
4. 授权 Emobot 访问您的 Gmail
5. 认证成功后，token 会自动保存

## 注意事项

- **安全性**：请妥善保管您的 OAuth 凭据，不要将其提交到版本控制系统
- **权限范围**：Emobot 需要以下权限：
  - 读取邮件
  - 发送邮件
  - 修改邮件标签
- **Token 管理**：认证 token 会自动刷新，无需手动管理
- **端口配置**：Gmail 认证使用 8081 端口，Emobot 服务器使用 8080 端口

## 故障排除

### 常见错误

1. **"invalid_client" 错误**
   - 检查 `gmail_credentials.json` 文件是否正确放置
   - 确认凭据文件中的 `client_id` 和 `client_secret` 正确

2. **"redirect_uri_mismatch" 错误**
   - 确保 `gmail_config.yaml` 中的 `redirect_uri` 设置为 `http://localhost:8081/oauth/callback`
   - 在 Google Cloud Console 中添加此重定向 URI

3. **"access_denied" 错误**
   - 确保您已在 OAuth 同意屏幕中添加了您的邮箱作为测试用户

4. **端口冲突错误**
   - 确保 Emobot 服务器运行在 8080 端口
   - Gmail 认证使用 8081 端口

### 获取帮助

如果遇到问题，请检查：
- Google Cloud Console 中的项目设置
- OAuth 同意屏幕配置
- 凭据文件的完整性
- 网络连接和防火墙设置
- 端口配置是否正确

## 测试连接

设置完成后，您可以使用以下命令测试 Gmail 连接：

```python
from tools.mcp_server.gmail_auth import GmailAuthManager

auth_manager = GmailAuthManager()
if auth_manager.test_connection():
    print("✅ Gmail 连接成功！")
else:
    print("❌ Gmail 连接失败")
``` 