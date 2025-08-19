# 多模型配置指南

Emobot 现在支持多种 AI 模型的自动切换，包括 OpenAI GPT、Google Gemini 和本地模型。

## 支持的模型

### 1. OpenAI GPT 模型
- **模型**: gpt-4, gpt-3.5-turbo, gpt-4o
- **特点**: 功能强大，支持工具调用
- **配置**: 需要 OpenAI API 密钥

### 2. Google Gemini 模型
- **模型**: gemini-1.5-pro, gemini-1.5-flash, gemini-pro
- **特点**: 性能优秀，价格相对较低
- **配置**: 需要 Google API 密钥

### 3. 本地模型
- **模型**: local
- **特点**: 无需 API 密钥，隐私保护
- **配置**: 无需额外配置

## 配置步骤

### 步骤 1: 获取 API 密钥

#### OpenAI API 密钥
1. 访问 [OpenAI API 页面](https://platform.openai.com/api-keys)
2. 注册账号并创建 API 密钥
3. 复制 API 密钥

#### Google Gemini API 密钥
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建 API 密钥
3. 复制 API 密钥

### 步骤 2: 配置环境变量

复制环境变量示例文件：
```bash
cp .env-multi-model .env
```

编辑 `.env` 文件，配置您的 API 密钥：

```bash
# OpenAI API 配置
OPENAI_API_KEY=your-actual-openai-api-key

# Google Gemini API 配置
GOOGLE_API_KEY=your-actual-google-api-key

# 默认模型（优先级：openai > gemini > local）
DEFAULT_MODEL=gpt-4
```

### 步骤 3: 运行程序

```bash
python main.py
```

## 自动故障转移机制

Emobot 具有智能的故障转移机制：

1. **优先级顺序**: OpenAI > Google Gemini > 本地模型
2. **自动检测**: 程序会自动检测可用的模型
3. **故障转移**: 当某个模型不可用时，自动切换到下一个可用模型
4. **状态监控**: 实时监控模型状态和连接情况

## 模型状态检查

在 Emobot 运行时，您可以使用以下命令检查模型状态：

```
/models
```

这将显示：
- 当前使用的模型
- 可用的模型提供商
- 各提供商的状态

## 手动切换模型

您可以在运行时手动切换模型：

```
/switch_model gemini-1.5-pro
```

## 配置示例

### 仅使用 OpenAI
```bash
OPENAI_API_KEY=your-openai-key
DEFAULT_MODEL=gpt-4
```

### 仅使用 Google Gemini
```bash
GOOGLE_API_KEY=your-google-key
DEFAULT_MODEL=gemini-1.5-pro
```

### 多模型备用
```bash
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
DEFAULT_MODEL=gpt-4
```

## 故障排除

### OpenAI 连接失败
- 检查 API 密钥是否正确
- 确认网络连接正常
- 检查 API 配额是否充足

### Google Gemini 连接失败
- 检查 API 密钥是否正确
- 确认已启用 Gemini API
- 检查网络连接

### 所有模型都失败
- 检查网络连接
- 确认 API 密钥配置正确
- 查看日志获取详细错误信息

## 性能对比

| 模型 | 响应速度 | 准确性 | 成本 | 工具支持 |
|------|----------|--------|------|----------|
| GPT-4 | 中等 | 高 | 高 | 完整 |
| GPT-3.5 | 快 | 中等 | 中等 | 完整 |
| Gemini Pro | 快 | 高 | 低 | 部分 |
| 本地模型 | 慢 | 中等 | 免费 | 有限 |

## 最佳实践

1. **配置多个 API 密钥**: 确保服务的高可用性
2. **监控使用量**: 定期检查 API 使用情况
3. **选择合适的模型**: 根据任务需求选择最适合的模型
4. **测试故障转移**: 定期测试自动切换功能

## 更新日志

- **v1.0**: 初始版本，支持 OpenAI GPT
- **v1.1**: 添加 Google Gemini 支持
- **v1.2**: 添加本地模型支持
- **v1.3**: 改进故障转移机制 