# Emobot - Personal Assistant

Emobot is a personal assistant bot with emotional responses, designed to provide a more engaging and personalized experience.

## Features

- 🤖 Personal assistant with personality and emotions
- 💬 Telegram integration
- 🎤 Voice message processing
- ⏰ Time and calendar functions
- 🔍 Web search capabilities (coming soon)
- 📝 Task management (coming soon)
- 📧 Email handling (coming soon)

## Project Structure

```
emobot/
├── core/                 # Core functionality
├── integrations/         # Platform interfaces
├── agents/               # Specialized functionality
├── services/             # External service connections
├── utils/                # Utility functions
├── data/                 # User data storage
└── tests/                # Test suite
```

## Installation

### Prerequisites

- Python 3.7 or higher
- ffmpeg (for voice message processing)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/emobot.git
   cd emobot
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```
   pip install -e .
   ```

4. Create a `.env` file:
   ```
   cp .env.example .env
   ```

5. Edit `.env` and add your API keys and tokens.

## Usage

### Telegram Bot

To start the Telegram bot:

```
emobot --telegram
```

Or run the module directly:

```
python -m emobot.main --telegram
```

### Command-line Options

- `--telegram`: Start the Telegram bot
- `--token TOKEN`: Use a specific Telegram token (overrides .env)
- `--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: Set logging level

## Development

### Adding New Features

1. Implement new agents in the `agents/` directory
2. Register them with the assistant agent in `core/assistant_agent.py`
3. Add any necessary service integrations in the `services/` directory

### Testing

```
python -m unittest discover -s tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.