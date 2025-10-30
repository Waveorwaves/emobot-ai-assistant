# Emobot AI Assistant

An intelligent AI assistant with calendar, email, and todo management capabilities.

## Features

- 💬 **Chat Interface** - Natural language interaction with AI
- 📅 **Calendar** - Google Calendar integration
- 📧 **Email** - Gmail integration
- ✅ **Todo List** - Task management
- 📊 **Dashboard** - Overview of all features

## Quick Start

### One-Command Setup

```bash
chmod +x start-integrated.sh
./start-integrated.sh
```

Then open: **http://localhost:3000**

## Prerequisites

- Python 3.8+
- Node.js 16+
- Gmail API credentials

## Installation

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd emobot-yifei
```

2. **Add Gmail credentials**:
   - Get `gmail_credentials.json` from Google Cloud Console
   - Place in `emobot/` directory

3. **Run the startup script**:
```bash
chmod +x start-integrated.sh
./start-integrated.sh
```

## Project Structure

```
emobot-yifei/
├── emobot/                  # Python Flask backend
│   ├── agent/              # AI reasoning module
│   ├── tools/              # MCP tools (calendar, email, todo)
│   ├── configs/            # Configuration files
│   ├── web_app.py          # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── gmail_credentials.json  # Gmail API credentials
├── frontend/               # React frontend
│   ├── src/               # Source code
│   ├── package.json       # Node dependencies
│   └── vite.config.ts     # Vite configuration
└── start-integrated.sh    # Startup script
```

## Manual Setup

### Backend

```bash
cd emobot
pip install -r requirements.txt
python web_app.py
```

Backend runs on: **http://localhost:8000**

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: **http://localhost:3000**

## Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials
5. Download credentials as `gmail_credentials.json`
6. Place in `emobot/` directory

## API Endpoints

### Chat
- `POST /api/chat` - Send chat message
- `POST /api/query` - Query with reasoning

### Calendar
- `GET /api/calendar/events` - List events
- `POST /api/calendar/events` - Create event

### Email
- `GET /api/email/list` - List emails
- `POST /api/email/send` - Send email
- `GET /api/email/read/<id>` - Read email

### Todo
- `GET /api/todo/list` - List todos
- `POST /api/todo/add` - Add todo
- `PUT /api/todo/update/<id>` - Update todo
- `DELETE /api/todo/delete/<id>` - Delete todo

## Troubleshooting

### Port Already in Use
The startup script automatically kills processes on ports 3000, 8000, and 8080.

Manual cleanup:
```bash
lsof -ti :8000 | xargs kill
lsof -ti :3000 | xargs kill
```

### Backend Won't Start
1. Check Python: `python --version`
2. Install dependencies: `pip install -r emobot/requirements.txt`
3. Check `gmail_credentials.json` exists in `emobot/`

### Frontend Won't Start
1. Check Node.js: `node --version`
2. Install dependencies: `cd frontend && npm install`
3. Check backend is running on port 8000

## Technologies

### Backend
- Python 3.8+
- Flask
- Google API Client (Gmail, Calendar)
- Gemini AI

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Axios

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
