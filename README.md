# Emobot AI Assistant

A full-stack personal AI assistant with Gmail, Google Calendar, and task management — built on a Flask backend with a React/TypeScript frontend.

## Features

- **Chat** — Natural language interface powered by LLM and smolagents
- **Email** — Gmail integration: read, draft, and send
- **Calendar** — Google Calendar integration: view and create events
- **Tasks** — Todo management with AI-assisted prioritization
- **Dashboard** — Unified overview of all tools
- **Memory** — Episodic memory module for personalized, context-aware responses

## Quick Start

```bash
chmod +x start-integrated.sh
./start-integrated.sh
```

Open **http://localhost:3000**

## Prerequisites

- Python 3.8+
- Node.js 16+
- Gmail API credentials (OAuth 2.0)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Waveorwaves/emobot-ai-assistant
cd emobot-ai-assistant
```

2. Set up credentials — copy the example config and fill in your values:
```bash
cp emobot/configs/gmail_config.example.yaml emobot/configs/gmail_config.yaml
cp .env.example .env
```

3. Get Gmail/Calendar OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/), enable the Gmail API and Calendar API, and download `gmail_credentials.json` into `emobot/`.

4. Run:
```bash
chmod +x start-integrated.sh
./start-integrated.sh
```

## Manual Setup

**Backend:**
```bash
cd emobot
pip install -r requirements.txt
python web_app.py        # http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev              # http://localhost:3000
```

## Project Structure

```
emobot-ai-assistant/
├── emobot/                   # Python Flask backend
│   ├── agent/               # AI reasoning, memory, demo manager
│   ├── tools/               # MCP tools (Gmail, Calendar, Todo)
│   ├── configs/             # Config files and examples
│   ├── demo_data/           # Seed data for demo mode
│   ├── web_app.py           # Main Flask application
│   └── requirements.txt
├── frontend/                # React + TypeScript frontend
│   ├── src/
│   └── vite.config.ts
├── start-integrated.sh      # One-command startup
├── .env.example
└── SECURITY.md
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a chat message |
| GET | `/api/calendar/events` | List calendar events |
| POST | `/api/calendar/events` | Create an event |
| GET | `/api/email/list` | List emails |
| POST | `/api/email/send` | Send an email |
| GET | `/api/todo/list` | List todos |
| POST | `/api/todo/add` | Add a todo |

## Stack

Python · Flask · Gemini AI · smolagents · Google APIs · React 18 · TypeScript · Vite · Tailwind CSS

## License

MIT
