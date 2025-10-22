"""
Web Application for Emobot
Provides HTTP API and simple web interface
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, render_template_string

# Try to import CORS, make it optional
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("⚠️  flask-cors not installed. CORS will not be enabled.")
    print("   Install with: pip install flask-cors")
import threading
import time

from agent.reasoning import ReasoningModule
from agent.reasoning_wrapper import ReasoningWrapper
from agent.actions import ActionExecutor
from tools.mcp_server.server import MCPToolServer
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Enable CORS if available
if CORS_AVAILABLE:
    CORS(app)  # Enable CORS for frontend access
    print("✅ CORS enabled for cross-origin requests")

# Global variables
reasoning_module = None
reasoning_wrapper = None
mcp_server_thread = None
server_url = "http://127.0.0.1:8080"

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Emobot - AI Assistant</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 800px;
            height: 600px;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 20px 20px 0 0;
            text-align: center;
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { font-size: 14px; opacity: 0.9; }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f7f7f7;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user { justify-content: flex-end; }
        .message.bot { justify-content: flex-start; }
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.user .message-content {
            background: #667eea;
            color: white;
        }
        .message.bot .message-content {
            background: white;
            color: #333;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .input-container {
            padding: 20px;
            background: white;
            border-radius: 0 0 20px 20px;
            border-top: 1px solid #e0e0e0;
        }
        .input-form {
            display: flex;
            gap: 10px;
        }
        #messageInput {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        #messageInput:focus {
            border-color: #667eea;
        }
        #sendButton {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        #sendButton:hover {
            transform: scale(1.05);
        }
        #sendButton:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .loading {
            display: none;
            padding: 12px 16px;
            background: white;
            border-radius: 18px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .loading.active { display: block; }
        .loading-dots {
            display: flex;
            gap: 5px;
        }
        .loading-dots span {
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Emobot</h1>
            <p>Your Intelligent AI Assistant</p>
        </div>
        <div class="chat-container" id="chatContainer">
            <div class="message bot">
                <div class="message-content">
                    Hello! I'm Emobot, your AI assistant. I can help you search the web, manage emails, create tasks, and more. How can I help you today?
                </div>
            </div>
        </div>
        <div class="input-container">
            <form class="input-form" id="chatForm">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="Type your message here..."
                    autocomplete="off"
                    required
                >
                <button type="submit" id="sendButton">Send</button>
            </form>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const chatForm = document.getElementById('chatForm');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        let loadingElement = null;

        function addMessage(content, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showLoading() {
            loadingElement = document.createElement('div');
            loadingElement.className = 'message bot';
            loadingElement.innerHTML = `
                <div class="loading active">
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            chatContainer.appendChild(loadingElement);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function hideLoading() {
            if (loadingElement) {
                loadingElement.remove();
                loadingElement = null;
            }
        }

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const message = messageInput.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, true);
            messageInput.value = '';
            
            // Disable input
            sendButton.disabled = true;
            messageInput.disabled = true;
            showLoading();

            try {
                // Send to API
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                
                hideLoading();
                
                if (data.success) {
                    addMessage(data.response, false);
                } else {
                    addMessage('Sorry, I encountered an error: ' + data.error, false);
                }
            } catch (error) {
                hideLoading();
                addMessage('Sorry, I could not connect to the server.', false);
                console.error('Error:', error);
            } finally {
                // Re-enable input
                sendButton.disabled = false;
                messageInput.disabled = false;
                messageInput.focus();
            }
        });

        // Focus input on load
        messageInput.focus();
    </script>
</body>
</html>
"""

def start_mcp_server():
    """Start MCP server in background thread"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        config_path = "configs/mcp.yaml"
        server = MCPToolServer(config_path)
        
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        server_config = config.get("server", {})
        
        print(f"✅ MCP server initialized with {len(server.tools)} tools")
        
        server.app.run(
            host=server_config.get("host", "127.0.0.1"),
            port=server_config.get("port", 8080),
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ MCP server error: {e}")

def initialize_agent(model_id="gemini-2.0-flash"):
    """Initialize the reasoning module"""
    global reasoning_module, reasoning_wrapper
    
    try:
        print(f"🤖 Initializing agent with model: {model_id}")
        reasoning_module = ReasoningModule(
            model_id=model_id,
            server_url=server_url,
            use_local_model=False
        )
        reasoning_wrapper = ReasoningWrapper(reasoning_module)
        print("✅ Agent initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/query', methods=['POST'])
def query():
    """Handle query requests (frontend compatible)"""
    try:
        data = request.json
        query_text = data.get('query', '').strip()
        session_id = data.get('session_id', 'default')
        model_id = data.get('model_id', 'gemini-2.0-flash')
        
        if not query_text:
            return jsonify({'success': False, 'error': 'Empty query'}), 400
        
        if not reasoning_wrapper:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Process query through reasoning wrapper (captures steps)
        result = reasoning_wrapper.process_query_with_steps(query_text)
        
        # Add session and model info
        result['session_id'] = session_id
        result['model_id'] = model_id
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Query error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'response': f'Error: {str(e)}',
            'error': str(e),
            'reasoning_steps': [
                {
                    'step': 1,
                    'type': 'error',
                    'message': str(e)
                }
            ]
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages (legacy endpoint)"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Empty message'}), 400
        
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Process query through reasoning module
        response = reasoning_module.process_query(message)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get available tools"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        tools = reasoning_module.action_executor.get_available_tools()
        return jsonify({
            'success': True,
            'tools': tools
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'agent_initialized': reasoning_module is not None,
        'mcp_server': server_url
    })

# Calendar API Endpoints
@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    """Get calendar events"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the list_events tool
        result = reasoning_module.action_executor.execute_tool('list_events', {})
        
        return jsonify({
            'success': True,
            'events': result if isinstance(result, list) else []
        })
    except Exception as e:
        logging.error(f"Calendar events error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calendar/events', methods=['POST'])
def create_calendar_event():
    """Create calendar event"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        title = data.get('title')
        time = data.get('time')
        duration = data.get('duration', '1 hour')
        description = data.get('description', '')
        
        if not title or not time:
            return jsonify({'success': False, 'error': 'Title and time required'}), 400
        
        # Use the create_event tool
        result = reasoning_module.action_executor.execute_tool('create_event', {
            'title': title,
            'time': time,
            'duration': duration,
            'description': description
        })
        
        return jsonify({
            'success': True,
            'message': 'Event created',
            'result': result
        })
    except Exception as e:
        logging.error(f"Create event error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Email API Endpoints
@app.route('/api/email/list', methods=['GET'])
def list_emails():
    """List emails"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the list_emails tool
        result = reasoning_module.action_executor.execute_tool('list_emails', {})
        
        return jsonify({
            'success': True,
            'emails': result if isinstance(result, list) else []
        })
    except Exception as e:
        logging.error(f"List emails error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/send', methods=['POST'])
def send_email():
    """Send email"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        
        if not to or not subject or not body:
            return jsonify({'success': False, 'error': 'To, subject, and body required'}), 400
        
        # Use the send_email tool
        result = reasoning_module.action_executor.execute_tool('send_email', {
            'to': to,
            'subject': subject,
            'body': body
        })
        
        return jsonify({
            'success': True,
            'message': 'Email sent',
            'result': result
        })
    except Exception as e:
        logging.error(f"Send email error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/read/<email_id>', methods=['GET'])
def read_email(email_id):
    """Read specific email"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the read_email tool
        result = reasoning_module.action_executor.execute_tool('read_email', {
            'email_id': email_id
        })
        
        return jsonify({
            'success': True,
            'email': result
        })
    except Exception as e:
        logging.error(f"Read email error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Todo API Endpoints
@app.route('/api/todo/list', methods=['GET'])
def list_todos():
    """List todo tasks"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the list_tasks tool
        result = reasoning_module.action_executor.execute_tool('list_tasks', {})
        
        return jsonify({
            'success': True,
            'todos': result if isinstance(result, list) else []
        })
    except Exception as e:
        logging.error(f"List todos error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/todo/add', methods=['POST'])
def add_todo():
    """Add todo task"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        title = data.get('title')
        description = data.get('description', '')
        priority = data.get('priority', 'medium')
        
        if not title:
            return jsonify({'success': False, 'error': 'Title required'}), 400
        
        # Use the add_task tool
        result = reasoning_module.action_executor.execute_tool('add_task', {
            'title': title,
            'description': description,
            'priority': priority
        })
        
        return jsonify({
            'success': True,
            'message': 'Task added',
            'result': result
        })
    except Exception as e:
        logging.error(f"Add todo error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/todo/update/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update todo task"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        
        # Use the update_task tool if available
        result = reasoning_module.action_executor.execute_tool('update_task', {
            'task_id': todo_id,
            **data
        })
        
        return jsonify({
            'success': True,
            'message': 'Task updated',
            'result': result
        })
    except Exception as e:
        logging.error(f"Update todo error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/todo/delete/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete todo task"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the delete_task tool if available
        result = reasoning_module.action_executor.execute_tool('delete_task', {
            'task_id': todo_id
        })
        
        return jsonify({
            'success': True,
            'message': 'Task deleted',
            'result': result
        })
    except Exception as e:
        logging.error(f"Delete todo error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Emobot Web Application")
    parser.add_argument('--model', type=str, default='gemini-2.0-flash', help='Model to use')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000, avoid 5000 due to macOS ControlCenter conflict)')
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 Starting Emobot Web Application")
    print("="*60)
    
    # Start MCP server in background
    print("📡 Starting MCP server...")
    global mcp_server_thread
    mcp_server_thread = threading.Thread(target=start_mcp_server, daemon=True)
    mcp_server_thread.start()
    
    # Wait for MCP server to start
    time.sleep(3)
    
    # Initialize agent
    if not initialize_agent(args.model):
        print("❌ Failed to start application")
        sys.exit(1)
    
    print("\n" + "="*60)
    print(f"✅ Emobot Web App is running!")
    print(f"🌐 Open your browser and go to:")
    print(f"   http://{args.host}:{args.port}")
    print("="*60 + "\n")
    
    # Start Flask web server
    app.run(
        host=args.host,
        port=args.port,
        debug=False,
        threaded=True
    )

if __name__ == '__main__':
    main()
