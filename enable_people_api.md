# 启用 Google People API 指南

## 问题描述
当前遇到错误："People API has not been used in project" 表明需要在 Google Cloud Console 中启用 People API。

## 解决步骤

### 1. 访问 Google Cloud Console
1. 打开 [Google Cloud Console](https://console.cloud.google.com/)
2. 确保选择了正确的项目（与你的 Gmail API 凭据相同的项目）

### 2. 启用 People API
1. 在左侧导航栏中，点击 "APIs & Services" > "Library"
2. 在搜索框中输入 "People API"
3. 点击 "Google People API"
4. 点击 "Enable" 按钮

### 3. 验证权限范围
确保你的 OAuth 同意屏幕包含以下权限：
- `https://www.googleapis.com/auth/contacts.readonly`
- `https://www.googleapis.com/auth/contacts`

### 4. 重新认证
1. 删除现有的 token 文件：
   ```bash
   rm emobot/gmail_token.json
   ```
2. 重新运行应用，它会提示你重新授权

### 5. 测试联系人功能
重新启动应用后，尝试：
- "what's Jason's email"
- "list my contacts"

## 替代方案

如果你不想启用 People API，可以：
1. 暂时禁用联系人功能
2. 使用邮件历史记录来查找联系人信息
3. 手动维护一个联系人列表

## 故障排除

### 如果仍然出现错误：
1. 确认项目 ID 正确
2. 检查 OAuth 同意屏幕配置
3. 确保账户有足够的权限
4. 等待几分钟让 API 启用生效

### 检查当前启用的 API：
1. 在 Google Cloud Console 中
2. 转到 "APIs & Services" > "Enabled APIs"
3. 确认 "People API" 在列表中

## 注意事项
- People API 有使用配额限制
- 首次启用可能需要几分钟生效
- 确保使用与 Gmail API 相同的 Google Cloud 项目
