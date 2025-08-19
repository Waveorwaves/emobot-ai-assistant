# 环境变量配置指南

本指南将帮助您正确配置 Emobot 的环境变量。

## 创建 .env 文件

### 方法 1：复制示例文件

```bash
# 在项目根目录执行
cp .env-example .env
```

### 方法 2：手动创建

```bash
# 创建新文件
touch .env

# 使用文本编辑器打开
nano .env  # 或使用 vim、code 等编辑器
```

## 必需配置

### API 密钥（至少配置一个）

#### 1. OpenAI API（推荐）

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**获取方式：**
1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 前往 API Keys 页面：https://platform.openai.com/api-keys
4. 点击 "Create new secret key"
5. 复制生成的密钥

**支持的模型：**
- `gpt-4` (最强大，但费用较高)
- `gpt-4-turbo` (性价比较高)
- `gpt-3.5-turbo` (最经济)

#### 2. Anthropic API（Claude）

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**获取方式：**
1. 访问 https://www.anthropic.com/
2. 申请 API 访问权限
3. 获取 API 密钥

**支持的模型：**
- `claude-3-opus` (最强大)
- `claude-3-sonnet` (平衡性能)
- `claude-3-haiku` (最快速)

#### 3. Hugging Face API

```env
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**获取方式：**
1. 访问 https://huggingface.co/
2. 注册/登录账号
3. 前往设置页面：https://huggingface.co/settings/tokens
4. 创建新的 Access Token

**支持的模型：**
- 开源模型如 Llama、Mistral 等

## 可选配置

### 基本配置

```env
# 日志级别
LOG_LEVEL=INFO  # 可选：DEBUG, INFO, WARNING, ERROR

# 默认模型
DEFAULT_MODEL=gpt-4  # 根据您的 API 选择

# 模型参数
MODEL_TEMPERATURE=0.7  # 0-1，控制创造性
MAX_TOKENS=2000  # 最大输出长度
```

### 网络代理（如需要）

```env
# HTTP 代理
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080

# 不使用代理的地址
NO_PROXY=localhost,127.0.0.1
```

### 高级配置

```env
# 记忆存储位置
MEMORY_DIR=agent_memory

# MCP 服务器配置
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8080

# 搜索工具配置
DUCKDUCKGO_REGION=cn-zh  # 搜索地区
DUCKDUCKGO_SAFESEARCH=moderate  # 安全搜索

# 时区和语言
TIMEZONE=Asia/Shanghai
LANGUAGE=zh-CN
```

## 真实邮件配置（可选）

如果您想使用真实的邮件功能而非模拟：

### Gmail 示例

```env
# SMTP 发送邮件
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # 注意：使用应用专用密码

# IMAP 接收邮件
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-app-password
```

**获取 Gmail 应用专用密码：**
1. 启用两步验证：https://myaccount.google.com/security
2. 生成应用专用密码：https://myaccount.google.com/apppasswords

### 其他邮件服务商

**QQ 邮箱：**
```env
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
IMAP_SERVER=imap.qq.com
IMAP_PORT=993
```

**163 邮箱：**
```env
SMTP_SERVER=smtp.163.com
SMTP_PORT=25
IMAP_SERVER=imap.163.com
IMAP_PORT=993
```

## 完整示例

### 最小配置（仅 OpenAI）

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 推荐配置

```env
# API 密钥
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 基本设置
LOG_LEVEL=INFO
DEFAULT_MODEL=gpt-4
MODEL_TEMPERATURE=0.7
MAX_TOKENS=2000

# 中文优化
DUCKDUCKGO_REGION=cn-zh
LANGUAGE=zh-CN
TIMEZONE=Asia/Shanghai
```

### 开发配置

```env
# API 密钥
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 调试模式
LOG_LEVEL=DEBUG
DEBUG_MODE=true

# 使用更便宜的模型进行开发
DEFAULT_MODEL=gpt-3.5-turbo
MODEL_TEMPERATURE=0.5
MAX_TOKENS=1000
```

## 安全提示

1. **永远不要将 .env 文件提交到版本控制系统**
   - 确保 `.env` 在 `.gitignore` 中
   - 使用 `.env-example` 作为模板

2. **保护您的 API 密钥**
   - 不要在代码中硬编码密钥
   - 定期轮换密钥
   - 设置使用限额

3. **权限管理**
   ```bash
   # 设置只有所有者可读写
   chmod 600 .env
   ```

## 故障排查

### 问题：找不到 API 密钥

**错误信息：**
```
未设置 OPENAI_API_KEY，请在 .env 文件中配置
```

**解决方案：**
1. 确认 .env 文件存在于项目根目录
2. 确认密钥格式正确（没有多余空格）
3. 重新运行程序

### 问题：API 调用失败

**可能原因：**
1. API 密钥无效
2. 网络连接问题
3. API 配额用尽

**解决方案：**
1. 验证密钥是否正确
2. 检查网络连接
3. 查看 API 使用情况

### 问题：代理设置不生效

**解决方案：**
```env
# 确保格式正确
HTTP_PROXY=http://username:password@proxy:port
HTTPS_PROXY=http://username:password@proxy:port
```

## 下一步

配置完成后，您可以：

1. 运行测试确保配置正确：
   ```bash
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key 已配置' if os.getenv('OPENAI_API_KEY') else '未找到 API Key')"
   ```

2. 启动 Emobot：
   ```bash
   ./run.sh  # 或 python main.py
   ```

3. 查看更多文档：
   - [README.md](../README.md) - 项目概览
   - [examples/demo.py](../examples/demo.py) - 使用示例 