# Emobot Web Application Guide

## Overview

This guide shows you how to run Emobot as a web application instead of a CLI app.

## Quick Start

### 1. Install Dependencies

```bash
cd ~/Documents\ \(Mac\)/Capstone/emobot-yifei/emobot
source ../venv/bin/activate
pip install flask-cors
```

### 2. Run the Web App

```bash
python web_app.py --model gemini-2.0-flash
```

### 3. Open in Browser

Open your browser and go to:
```
http://127.0.0.1:8000
```

**Note:** We use port 8000 instead of 5000 because macOS ControlCenter often occupies port 5000.

You should see a beautiful chat interface!

## Features

✅ **Modern Web UI** - Clean, responsive chat interface  
✅ **Real-time Chat** - Instant responses from the AI  
✅ **All Tools Available** - Web search, email, calendar, todo  
✅ **Mobile Friendly** - Works on phones and tablets  
✅ **No Installation** - Just open in browser  

## Configuration Options

### Change Port

```bash
python web_app.py --port 3000
```

### Use Different Model

```bash
python web_app.py --model gemini-1.5-pro
```

### Allow External Access

```bash
python web_app.py --host 0.0.0.0 --port 8000
```

Then access from other devices on your network:
```
http://YOUR_IP_ADDRESS:8000
```

## API Endpoints

The web app also exposes REST API endpoints:

### POST /api/chat
Send a message to the AI

**Request:**
```json
{
  "message": "search for AI news"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Here are the latest AI news..."
}
```

### GET /api/tools
Get available tools

**Response:**
```json
{
  "success": true,
  "tools": [
    {
      "name": "web_search",
      "description": "Performs web search...",
      "parameters": {...}
    }
  ]
}
```

### GET /api/health
Health check

**Response:**
```json
{
  "status": "ok",
  "agent_initialized": true,
  "mcp_server": "http://127.0.0.1:8080"
}
```

## Using the API with curl

```bash
# Send a chat message
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "what is AI?"}'

# Get available tools
curl http://127.0.0.1:8000/api/tools

# Health check
curl http://127.0.0.1:8000/api/health
```

## Using the API with JavaScript

```javascript
// Send a message
async function sendMessage(message) {
  const response = await fetch('http://127.0.0.1:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: message })
  });
  
  const data = await response.json();
  console.log(data.response);
}

sendMessage('search for Python tutorials');
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Browser                        │
│  http://127.0.0.1:8000                         │
└──────────────────┬──────────────────────────────┘
                   │ HTTP
                   ▼
┌─────────────────────────────────────────────────┐
│         Flask Web Server (Port 8000)            │
│  ┌───────────────────────────────────────────┐ │
│  │  Routes:                                   │ │
│  │  - GET  /           → Web UI              │ │
│  │  - POST /api/chat   → Process message     │ │
│  │  - GET  /api/tools  → List tools          │ │
│  │  - GET  /api/health → Health check        │ │
│  └───────────────────────────────────────────┘ │
│                      ↕                          │
│  ┌───────────────────────────────────────────┐ │
│  │  Reasoning Module                         │ │
│  │  (Same as CLI version)                    │ │
│  └───────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────┘
                   │ HTTP
                   ▼
┌─────────────────────────────────────────────────┐
│      MCP Server (Port 8080)                     │
│  - web_search                                   │
│  - email                                        │
│  - todo_list                                    │
│  - calendar                                     │
└─────────────────────────────────────────────────┘
```

## Comparison: CLI vs Web App

| Feature | CLI App | Web App |
|---------|---------|---------|
| **Interface** | Terminal | Browser |
| **Access** | Local only | Can be remote |
| **UI** | Text-based | Graphical |
| **Multiple Users** | No | Yes (with modifications) |
| **Mobile** | No | Yes |
| **Easy to Share** | No | Yes |
| **Installation** | Python required | Just open URL |

## Next Steps

### Option 1: Deploy to Cloud

Deploy to Heroku, Railway, or Render:

```bash
# Create Procfile
echo "web: python web_app.py --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy to Heroku
heroku create emobot-app
git push heroku main
```

### Option 2: Add Authentication

Add user login to protect your AI:

```python
from flask_login import LoginManager, login_required

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    # ... existing code
```

### Option 3: Add Database

Store conversation history:

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text)
    bot_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
```

### Option 4: Build React Frontend

Create a more advanced UI with React:

```bash
cd emobot-yifei
npx create-react-app frontend
cd frontend
npm install axios
```

Then build a React chat interface that calls the API.

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>
```

### CORS Errors

If you get CORS errors when accessing from a different domain:

```python
# In web_app.py, update CORS config
CORS(app, origins=['http://your-frontend-domain.com'])
```

### Agent Not Responding

Check if MCP server is running:

```bash
curl http://127.0.0.1:8080/tools
```

Should return list of tools.

## Production Deployment

For production use, add:

1. **HTTPS** - Use SSL certificates
2. **Authentication** - Require login
3. **Rate Limiting** - Prevent abuse
4. **Logging** - Track usage
5. **Error Handling** - Better error messages
6. **Database** - Store conversations
7. **Caching** - Speed up responses
8. **Load Balancing** - Handle multiple users

Example with gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

## Summary

You now have three ways to run Emobot:

1. **CLI App** - `python main.py`
2. **Web App** - `python web_app.py`
3. **API Server** - Use the REST API endpoints

Choose based on your needs:
- **CLI**: Quick testing, personal use
- **Web App**: Share with others, better UI
- **API**: Integrate with other apps
