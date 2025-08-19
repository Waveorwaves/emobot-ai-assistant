# Emobot - Intelligent Assistant

Emobot is a super intelligent assistant based on large language models, implementing the ReAct (Reasoning + Acting) framework for enhanced reasoning and tool usage capabilities.

## Features

- **ReAct Loop**: Implements the Reasoning + Acting loop for step-by-step problem solving
- **Multi-Model Support**: Supports various language models including Gemini, GPT, and local models
- **Tool Integration**: Integrated with MCP (Model Context Protocol) tools for web search, email management, and task management
- **Memory System**: Advanced memory management with short-term and long-term memory
- **Planning Phase**: Pre-execution planning for complex tasks
- **Real-time Tool Execution**: Live interaction with external services

## Architecture

```
Emobot/
├── agent/                 # Core agent modules
│   ├── reasoning.py      # ReAct reasoning engine
│   ├── perception.py     # Input processing
│   ├── memory.py         # Memory management
│   ├── actions.py        # Tool execution
│   └── model_manager.py  # Model management
├── tools/                # MCP tool implementations
│   └── mcp_server/       # MCP server and tools
├── configs/              # Configuration files
└── tests/                # Test files
```

## Quick Start

### Prerequisites

- Python 3.8+
- Required API keys (Gemini, OpenAI, etc.)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd emobot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
```bash
cp configs/gmail_config.example.yaml configs/gmail_config.yaml
# Edit the configuration file with your API keys
```

### Running Emobot

Start the application:
```bash
python main.py --model gemini-1.5-flash
```

## Usage

### Basic Commands

- `/help` - Show available commands
- `/stats` - Show execution statistics
- `/memory` - Show memory system status
- `/tools` - List available tools
- `/health` - Check system health
- `/exit` - Exit the application

## Configuration

### Model Configuration

Edit `configs/local_model_config.yaml` to configure different models:

```yaml
models:
  gemini-1.5-flash:
    api_key: ${GEMINI_API_KEY}
    max_tokens: 4096
  gpt-4:
    api_key: ${OPENAI_API_KEY}
    max_tokens: 4096
```

### Gmail Configuration

Configure Gmail integration in `configs/gmail_config.yaml`:

```yaml
gmail:
  client_id: your_client_id
  client_secret: your_client_secret
  redirect_uri: http://localhost:8080/callback
  scopes:
    - https://www.googleapis.com/auth/gmail.readonly
    - https://www.googleapis.com/auth/gmail.send
    - https://www.googleapis.com/auth/gmail.modify
  user_email: your_email@gmail.com
```

## Development

### Project Structure

- **agent/**: Core agent implementation
- **tools/**: MCP tool implementations
- **configs/**: Configuration files
- **tests/**: Test files and examples
- **docs/**: Documentation

### Adding New Tools

1. Create a new tool in `tools/mcp_server/`
2. Register the tool in `tools/mcp_server/server.py`
3. Update the system prompt in `configs/system_prompt.md`

## License

This project is licensed under the MIT License