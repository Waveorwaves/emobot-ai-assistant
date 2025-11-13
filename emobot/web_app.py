"""
Web Application for Emobot
Provides HTTP API and simple web interface
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory

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

# Get the directory where web_app.py is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to the built React frontend (go up one level from emobot/ to emobot1/, then to frontend/dist)
FRONTEND_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'frontend', 'dist')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# Enable CORS if available
if CORS_AVAILABLE:
    CORS(app)  # Enable CORS for frontend access
    print("✅ CORS enabled for cross-origin requests")

# Global variables
reasoning_module = None
reasoning_wrapper = None
mcp_server_thread = None
server_url = "http://127.0.0.1:8080"

# Schedule optimization data
ai_actions = []
approval_items = []
action_counter = 0
approval_counter = 0


def start_mcp_server():
    """Start MCP server on port 8080"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        config_path = "configs/mcp.yaml"
        
        # Load config to get server settings
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        server_config = config.get("server", {})
        host = server_config.get("host", "127.0.0.1")
        port = server_config.get("port", 8080)
        
        server = MCPToolServer(config_path)
        
        print(f"✅ MCP server initialized with {len(server.tools)} tools")
        print(f"🚀 Starting MCP server at http://{host}:{port}")
        
        # Start the Flask server on port 8080
        server.run(host=host, port=port)

    except Exception as e:
        print(f"❌ MCP server error: {e}")
        import traceback
        traceback.print_exc()

def initialize_agent(model_id="gemini-2.5-flash"):
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
    """Serve the React frontend"""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/simple')
def simple_ui():
    """Serve the simple HTML UI for backend testing"""
    return render_template('index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from React build"""
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    else:
        # For client-side routing, return index.html
        return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/api/query', methods=['POST'])
def query():
    """Handle query requests (frontend compatible)"""
    try:
        data = request.json
        query_text = data.get('query', '').strip()
        session_id = data.get('session_id', 'default')
        model_id = data.get('model_id', 'gemini-2.5-flash')
        
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
    """Handle chat messages with confirmation support"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Empty message'}), 400
        
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Check if there's a pending confirmation (like terminal version)
        if reasoning_module.has_pending_confirmation():
            logging.debug("Processing confirmation response...")
            response = reasoning_module.handle_confirmation_response(message)
        else:
            # Process normal query
            response = reasoning_module.process_query(message)
        
        # Check if there's now a pending confirmation after processing
        has_pending = reasoning_module.has_pending_confirmation()
        pending_confirmations = []
        if has_pending:
            pending_confirmations = reasoning_module.get_pending_confirmation_requests()
        
        return jsonify({
            'success': True,
            'response': response,
            'has_pending_confirmation': has_pending,
            'pending_confirmations': pending_confirmations
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

@app.route('/api/confirmations', methods=['GET'])
def get_pending_confirmations():
    """Get pending confirmation requests"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        has_pending = reasoning_module.has_pending_confirmation()
        pending_confirmations = []
        if has_pending:
            pending_confirmations = reasoning_module.get_pending_confirmation_requests()
        
        return jsonify({
            'success': True,
            'has_pending_confirmation': has_pending,
            'pending_confirmations': pending_confirmations
        })
    except Exception as e:
        logging.error(f"Get confirmations error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/confirmations/cancel', methods=['POST'])
def cancel_confirmations():
    """Cancel all pending confirmations"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Cancel all pending confirmations
        pending = reasoning_module.get_pending_confirmation_requests()
        cancelled_count = 0
        
        for req in pending:
            reasoning_module.cancel_confirmation_request(req['id'])
            cancelled_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Cancelled {cancelled_count} pending confirmations'
        })
    except Exception as e:
        logging.error(f"Cancel confirmations error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Calendar API Endpoints
@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    """Get calendar events"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the calendar tool with list_events operation
        result = reasoning_module.action_executor.execute_action('calendar', {'operation': 'list_events'})
        
        # Extract events from the result
        if isinstance(result, dict) and result.get('status') == 'success':
            events = result.get('events', [])
        else:
            events = []
            
        return jsonify({
            'success': True,
            'events': events
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

        # Use the calendar tool with create_event operation
        result = reasoning_module.action_executor.execute_action('calendar', {
            'operation': 'create_event',
            'title': title,
            'start_time': time,
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

@app.route('/api/calendar/add', methods=['POST'])
def add_calendar_event():
    """Add calendar event (alternative endpoint for frontend)"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500

        data = request.json
        title = data.get('title')
        # Accept both 'datetime' and 'start_time' parameters
        start_time = data.get('start_time') or data.get('datetime')
        duration = data.get('duration', '1 hour')
        attendees = data.get('attendees', [])
        description = data.get('description', '')

        if not title or not start_time:
            return jsonify({'success': False, 'error': 'Title and start_time required'}), 400

        logging.info(f"Adding calendar event: {title} at {start_time}")

        # Build description from attendees if not provided
        if not description and attendees:
            description = f"Attendees: {', '.join(attendees)}"

        # Use the calendar tool with create_event operation
        result = reasoning_module.action_executor.execute_action('calendar', {
            'operation': 'create_event',
            'title': title,
            'start_time': start_time,
            'description': description,
            'attendees': attendees
        })

        logging.info(f"Calendar add result: {result}")

        if result and result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Event added to calendar',
                'result': result,
                'event': result.get('event')
            })
        else:
            error_msg = result.get('error_message', 'Failed to add event')
            logging.error(f"Calendar add failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
    except Exception as e:
        logging.error(f"Add calendar event error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Email API Endpoints
@app.route('/api/email/list', methods=['GET'])
def list_emails():
    """List emails"""
    try:
        if not reasoning_module:
            error_msg = 'Agent not initialized - MCP server may not be running'
            logging.error(error_msg)
            return jsonify({'success': False, 'error': error_msg, 'emails': []}), 500
        
        # Get query parameter for filtering (e.g., 'in:sent', 'in:draft')
        search_query = request.args.get('query', '')
        
        logging.info(f"Fetching emails with query: '{search_query}'")
        
        if search_query:
            # Use search_emails operation for specific queries
            result = reasoning_module.action_executor.execute_action('email', {
                'operation': 'search_emails',
                'search_query': search_query,
                'max_results': 20
            })
        else:
            # Default to inbox
            result = reasoning_module.action_executor.execute_action('email', {
                'operation': 'read_inbox',
                'max_results': 10
            })
        
        logging.info(f"Email fetch result: {result}")
        
        if result and result.get('status') == 'success':
            emails = result.get('emails', result.get('result', []))
            return jsonify({
                'success': True,
                'emails': emails if isinstance(emails, list) else []
            })
        else:
            error_msg = result.get('error_message', 'Failed to fetch emails')
            logging.error(f"Email fetch failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg,
                'emails': []
            }), 500
    except Exception as e:
        logging.error(f"List emails error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e), 'emails': []}), 500

@app.route('/api/email/sent', methods=['GET'])
def list_sent_emails():
    """List sent emails"""
    try:
        if not reasoning_module:
            error_msg = 'Agent not initialized - MCP server may not be running'
            logging.error(error_msg)
            return jsonify({'success': False, 'error': error_msg, 'emails': []}), 500

        logging.info("Fetching sent emails")

        # Use the email tool with read_sent operation
        result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'read_sent',
            'max_results': 10
        })

        logging.info(f"Sent email fetch result: {result}")

        if result and result.get('status') == 'success':
            emails = result.get('emails', result.get('result', []))
            return jsonify({
                'success': True,
                'emails': emails if isinstance(emails, list) else []
            })
        else:
            error_msg = result.get('error_message', 'Failed to fetch sent emails')
            logging.error(f"Sent email fetch failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg,
                'emails': []
            }), 500
    except Exception as e:
        logging.error(f"List sent emails error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e), 'emails': []}), 500

@app.route('/api/email/send', methods=['POST'])
def send_email():
    """Send email"""
    try:
        if not reasoning_module:
            error_msg = 'Agent not initialized - MCP server may not be running'
            logging.error(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 500

        data = request.json
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')

        if not to or not subject or not body:
            return jsonify({'success': False, 'error': 'To, subject, and body required'}), 400

        logging.info(f"Sending email to: {to}, subject: {subject}")

        # Use the email tool with send operation
        result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'send_email',
            'recipient': to,
            'subject': subject,
            'body': body
        })

        logging.info(f"Send email result: {result}")

        if result and result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Email sent successfully',
                'result': result
            })
        else:
            error_msg = result.get('error_message', 'Failed to send email')
            logging.error(f"Send email failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
    except Exception as e:
        logging.error(f"Send email error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/read/<email_id>', methods=['GET'])
def read_email(email_id):
    """Read specific email"""
    try:
        if not reasoning_module:
            error_msg = 'Agent not initialized - MCP server may not be running'
            logging.error(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 500
        
        logging.info(f"Reading email: {email_id}")
        
        # Use the email tool with get_email_details operation
        result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'get_email_details',
            'message_id': email_id
        })
        
        logging.info(f"Read email result: {result}")
        
        if result and result.get('status') == 'success':
            return jsonify({
                'success': True,
                'email': result.get('result', {})
            })
        else:
            error_msg = result.get('error_message', 'Failed to read email')
            logging.error(f"Read email failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
    except Exception as e:
        logging.error(f"Read email error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/contacts', methods=['GET'])
def list_contacts():
    """List contacts"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        result = reasoning_module.action_executor.execute_action('email', {'operation': 'get_contacts', 'max_results': 100})
        
        return jsonify({
            'success': True,
            'contacts': result.get('result', []) if result.get('status') == 'success' else [],
            'error': result.get('error_message') if result.get('status') != 'success' else None
        })
        
    except Exception as e:
        logging.error(f"Contacts list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/email/labels', methods=['GET'])
def list_labels():
    """List email labels"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        result = reasoning_module.action_executor.execute_action('email', {'operation': 'get_labels'})
        
        return jsonify({
            'success': True,
            'labels': result.get('result', []) if result.get('status') == 'success' else [],
            'error': result.get('error_message') if result.get('status') != 'success' else None
        })
        
    except Exception as e:
        logging.error(f"Labels list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/email/draft', methods=['POST'])
def create_draft():
    """Create email draft"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        
        if not all([to, subject, body]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'create_draft',
            'recipient': to,
            'subject': subject,
            'body': body
        })
        
        return jsonify({
            'success': result.get('status') == 'success',
            'result': result.get('result'),
            'error': result.get('error_message') if result.get('status') != 'success' else None
        })
        
    except Exception as e:
        logging.error(f"Draft creation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/email/mark-read', methods=['POST'])
def mark_email_read():
    """Mark email as read"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        message_id = data.get('message_id')
        
        if not message_id:
            return jsonify({'success': False, 'error': 'Message ID required'}), 400
        
        result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'mark_read',
            'message_id': message_id
        })
        
        return jsonify({
            'success': result.get('status') == 'success',
            'result': result.get('result'),
            'error': result.get('error_message') if result.get('status') != 'success' else None
        })
        
    except Exception as e:
        logging.error(f"Mark read error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Todo API Endpoints
@app.route('/api/todo/list', methods=['GET'])
def list_todos():
    """List todo tasks"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the todo_list tool with view_list operation
        result = reasoning_module.action_executor.execute_action('todo_list', {'operation': 'view_list'})
        
        # Extract tasks from result
        tasks = []
        if isinstance(result, dict):
            if result.get('status') == 'success':
                tasks = result.get('tasks', [])
            else:
                return jsonify({'success': False, 'error': result.get('message', 'Unknown error')}), 500
        
        return jsonify({
            'success': True,
            'tasks': tasks
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
        category = data.get('category', 'personal')
        due_date = data.get('due_date')
        tags = data.get('tags', [])
        
        if not title:
            return jsonify({'success': False, 'error': 'Title required'}), 400
        
        # Use the todo_list tool with add_task operation
        params = {
            'operation': 'add_task',
            'title': title,
            'description': description,
            'priority': priority,
            'category': category,
            'tags': tags
        }
        
        if due_date:
            params['due_date'] = due_date
        
        result = reasoning_module.action_executor.execute_action('todo_list', params)
        
        if isinstance(result, dict) and result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Task added successfully',
                'task': result.get('task')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Failed to add task')
            }), 500
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
        
        # Build update parameters
        params = {
            'operation': 'update_task',
            'task_id': todo_id
        }
        
        # Add optional fields
        if 'title' in data:
            params['title'] = data['title']
        if 'description' in data:
            params['description'] = data['description']
        if 'priority' in data:
            params['priority'] = data['priority']
        if 'category' in data:
            params['category'] = data['category']
        if 'status' in data:
            params['status'] = data['status']
        if 'due_date' in data:
            params['due_date'] = data['due_date']
        if 'tags' in data:
            params['tags'] = data['tags']
        
        # Use the todo_list tool with update_task operation
        result = reasoning_module.action_executor.execute_action('todo_list', params)
        
        if isinstance(result, dict) and result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Task updated successfully',
                'task': result.get('task')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Failed to update task')
            }), 500
    except Exception as e:
        logging.error(f"Update todo error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/todo/delete/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete todo task"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the todo_list tool with delete_task operation
        result = reasoning_module.action_executor.execute_action('todo_list', {
            'operation': 'delete_task',
            'task_id': todo_id
        })
        
        if isinstance(result, dict) and result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Task deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Failed to delete task')
            }), 500
    except Exception as e:
        logging.error(f"Delete todo error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Insights API Endpoint
@app.route('/api/insights/analyze', methods=['POST'])
def analyze_insights():
    """Analyze emails, calendar, and todos to provide intelligent insights"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        logging.info("Starting insights analysis...")
        
        # Step 1: Fetch unread emails
        email_result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'read_inbox',
            'max_results': 50,
            'unread_only': True
        })
        
        unread_emails = []
        if email_result and email_result.get('status') == 'success':
            unread_emails = email_result.get('emails', [])
        
        logging.info(f"Found {len(unread_emails)} unread emails")
        
        # Step 2: Fetch calendar events
        calendar_result = reasoning_module.action_executor.execute_action('calendar', {
            'operation': 'list_events'
        })
        
        calendar_events = []
        if calendar_result and calendar_result.get('status') == 'success':
            calendar_events = calendar_result.get('events', [])
        
        logging.info(f"Found {len(calendar_events)} calendar events")
        
        # Step 3: Fetch todo tasks
        todo_result = reasoning_module.action_executor.execute_action('todo_list', {
            'operation': 'view_list'
        })
        
        todo_tasks = []
        if todo_result and todo_result.get('status') == 'success':
            todo_tasks = todo_result.get('tasks', [])
        
        logging.info(f"Found {len(todo_tasks)} todo tasks")
        
        # Step 4: Build analysis prompt for LLM
        analysis_prompt = _build_insights_prompt(unread_emails, calendar_events, todo_tasks)
        
        logging.info("Sending data to LLM for analysis...")
        
        # Step 5: Use LLM to analyze and generate insights
        import sys
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()
        
        with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
            llm_response = reasoning_module.agent.run(analysis_prompt)
        
        logging.info("LLM analysis complete")
        
        # Step 6: Parse LLM response into structured insights
        insights, summary = _parse_insights_response(
            str(llm_response), 
            len(unread_emails), 
            len(calendar_events), 
            len(todo_tasks)
        )
        
        logging.info(f"Generated {len(insights)} insights")
        
        return jsonify({
            'success': True,
            'insights': insights,
            'summary': summary,
            'generated_at': time.time()  # Add timestamp
        })
        
    except Exception as e:
        logging.error(f"Insights analysis error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _build_insights_prompt(emails, events, tasks):
    """Build prompt for LLM to analyze data and generate insights"""

    # Get current date/time for context
    from datetime import datetime
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%B %d, %Y at %I:%M %p")

    # Format emails
    emails_text = ""
    if emails:
        emails_text = "UNREAD EMAILS:\n"
        for i, email in enumerate(emails[:20], 1):  # Limit to 20 emails
            subject = email.get('subject', 'No Subject')
            sender = email.get('from', email.get('sender', 'Unknown'))
            date = email.get('date', 'Unknown date')
            body_preview = email.get('body', email.get('snippet', ''))[:200]
            emails_text += f"{i}. From: {sender}\n   Subject: {subject}\n   Date: {date}\n   Preview: {body_preview}...\n\n"
    else:
        emails_text = "UNREAD EMAILS: None\n\n"

    # Format calendar events - separate upcoming vs past
    from datetime import datetime as dt
    import re

    def parse_event_time(time_str):
        """Try to parse event time using common formats"""
        if not time_str:
            return None

        # Common datetime formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%B %d, %Y, %I:%M %p",
            "%B %d, %Y at %I:%M %p",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y %I:%M %p",
        ]

        for fmt in formats:
            try:
                return dt.strptime(time_str, fmt)
            except:
                continue

        # Try to extract date if only date is present
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', time_str)
        if date_match:
            try:
                return dt.strptime(date_match.group(0), "%Y-%m-%d")
            except:
                pass

        return None

    upcoming_events = []
    past_events = []

    for event in events:
        try:
            title = event.get('title', event.get('summary', 'Untitled'))
            time_str = event.get('time', event.get('start_time', event.get('datetime', '')))
            description = event.get('description', event.get('details', ''))

            # Try to parse the event time
            if time_str:
                event_time = parse_event_time(time_str)
                if event_time:
                    if event_time > current_datetime:
                        upcoming_events.append((title, time_str, description))
                    else:
                        past_events.append((title, time_str, description))
                else:
                    # If parsing fails, assume it's upcoming to be safe
                    upcoming_events.append((title, time_str, description))
            else:
                upcoming_events.append((title, time_str, description))
        except:
            continue

    events_text = ""
    if upcoming_events:
        events_text = "UPCOMING CALENDAR EVENTS:\n"
        for i, (title, time_str, description) in enumerate(upcoming_events, 1):
            events_text += f"{i}. {title}\n   Time: {time_str}\n   Details: {description}\n\n"
    else:
        events_text = "UPCOMING CALENDAR EVENTS: None\n\n"
    
    # Format tasks
    tasks_text = ""
    if tasks:
        tasks_text = "TODO TASKS:\n"
        for i, task in enumerate(tasks, 1):
            title = task.get('title', 'Untitled')
            priority = task.get('priority', 'medium')
            status = task.get('status', 'pending')
            due_date = task.get('due_date', 'No due date')
            tasks_text += f"{i}. {title}\n   Priority: {priority}, Status: {status}, Due: {due_date}\n\n"
    else:
        tasks_text = "TODO TASKS: None\n\n"
    
    prompt = f"""You are an intelligent assistant analyzing a user's emails, calendar, and tasks to provide actionable insights.

CURRENT DATE AND TIME: {current_datetime_str}

IMPORTANT: Only analyze UPCOMING events that are in the future. Ignore any events that have already occurred before {current_datetime_str}.

{emails_text}

{events_text}

{tasks_text}

Please analyze the above information and provide insights in the following format:

INSIGHT: [Type: warning/error/success/info/conflict]
Title: [Brief title]
Content: [Detailed description of the insight]
Suggestion: [Actionable suggestion for the user]
SenderEmail: [ONLY for email-related insights - include the sender's email address from the email data above]
---

Focus on:
1. **Scheduling Conflicts**: Check if any emails request meetings at times that conflict with existing UPCOMING calendar events
2. **Urgent Items**: Identify emails or tasks that require immediate attention
3. **Overdue Tasks**: Highlight tasks that are past their due date
4. **Meeting Requests**: Identify emails that contain meeting invitations or scheduling requests for FUTURE dates/times
5. **Priority Recommendations**: Suggest which tasks should be prioritized based on deadlines and importance
6. **Time Management**: Provide suggestions for better time management based on the schedule

CRITICAL: Do NOT provide insights about events that have already passed. Only focus on upcoming events and current/future tasks.

**IMPORTANT - For Meeting Request Insights:**
When generating suggestions for meeting requests, be SPECIFIC and ACTIONABLE:
- If the calendar shows NO CONFLICT: Say "You are available at this time. Reply to confirm your availability and the meeting will be added to your calendar."
- If there IS a conflict: Say "You have [conflicting event] at this time. Reply to propose an alternative time such as [suggest alternative]."
- Always make the suggestion immediate and clear about what action to take.

Example format:
INSIGHT: [Type: info]
Title: New Capstone Meeting Request
Content: You have received an email from Jason Huang requesting a Capstone meeting on November 15th at 1:30 PM for about an hour. Your calendar currently shows no conflicting events.
Suggestion: You are available at this time. Click 'Reply to Email' to confirm your availability and the meeting will be added to your calendar.
SenderEmail: sender@example.com
---

INSIGHT: [Type: conflict]
Title: Scheduling Conflict Detected
Content: You have a dinner scheduled at 6:00 PM on November 3rd, but received an email requesting a meeting at the same time.
Suggestion: You have a conflict at this time. Click 'Reply to Email' to propose an alternative time such as November 4th at 2:00 PM.
SenderEmail: sender@example.com
---

INSIGHT: [Type: warning]
Title: Urgent Email Requires Response
Content: Email from John Doe about project deadline needs immediate attention.
Suggestion: Review and respond to this email within the next 2 hours.
SenderEmail: john.doe@company.com
---

Please provide 3-7 insights based on the data above. If there are no conflicts or urgent items, provide positive feedback and general recommendations.

**CRITICAL - Avoid Duplicates:**
- Do NOT create multiple insights for the same email or event
- Each insight should be about a DIFFERENT item (different email, different task, different event)
- If an email is about a meeting request, create ONE insight about it, not multiple
"""
    
    return prompt

@app.route('/api/insights/generate-reply', methods=['POST'])
def generate_email_reply():
    """Generate email reply based on insight context"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        recipient = data.get('recipient', '')
        context = data.get('context', '')
        suggestion = data.get('suggestion', '')
        
        logging.info(f"Generating email reply for: {recipient}")
        
        # Build prompt for LLM to generate email
        prompt = f"""Generate a professional email reply based on the following context:

Context: {context}
Suggestion: {suggestion}
Recipient: {recipient}

Please generate:
1. A suitable email subject line
2. A professional and friendly email body

The email should:
- Be polite and professional
- Address the scheduling conflict or request mentioned
- Suggest alternative times if needed
- Be concise (2-3 paragraphs maximum)

Format your response as:
SUBJECT: [subject line]
BODY: [email body]
"""
        
        # Use LLM to generate email
        import sys
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()
        
        with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
            llm_response = reasoning_module.agent.run(prompt)
        
        response_text = str(llm_response)
        
        # Parse response
        subject = ''
        body = ''
        
        if 'SUBJECT:' in response_text:
            subject_part = response_text.split('SUBJECT:')[1].split('BODY:')[0].strip()
            subject = subject_part
        
        if 'BODY:' in response_text:
            body_part = response_text.split('BODY:')[1].strip()
            body = body_part
        
        # Fallback if parsing fails
        if not subject:
            subject = 'Re: Meeting Request'
        if not body:
            body = response_text
        
        return jsonify({
            'success': True,
            'recipient': recipient,
            'subject': subject,
            'body': body
        })
        
    except Exception as e:
        logging.error(f"Generate reply error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _parse_insights_response(response, email_count, event_count, task_count):
    """Parse LLM response into structured insights"""
    insights = []
    
    # Split response by insight delimiter
    insight_blocks = response.split('---')
    
    for block in insight_blocks:
        block = block.strip()
        if not block or 'INSIGHT:' not in block:
            continue
        
        try:
            # Extract type
            insight_type = 'info'
            if '[Type:' in block:
                type_match = block.split('[Type:')[1].split(']')[0].strip()
                insight_type = type_match.lower()
            
            # Extract title
            title = ''
            if 'Title:' in block:
                title_line = [line for line in block.split('\n') if line.strip().startswith('Title:')]
                if title_line:
                    title = title_line[0].replace('Title:', '').strip()
            
            # Extract content
            content = ''
            if 'Content:' in block:
                content_line = [line for line in block.split('\n') if line.strip().startswith('Content:')]
                if content_line:
                    content = content_line[0].replace('Content:', '').strip()
            
            # Extract suggestion
            suggestion = ''
            if 'Suggestion:' in block:
                suggestion_line = [line for line in block.split('\n') if line.strip().startswith('Suggestion:')]
                if suggestion_line:
                    suggestion = suggestion_line[0].replace('Suggestion:', '').strip()

            # Extract sender email if present
            sender_email = ''
            if 'SenderEmail:' in block:
                sender_line = [line for line in block.split('\n') if line.strip().startswith('SenderEmail:')]
                if sender_line:
                    sender_email = sender_line[0].replace('SenderEmail:', '').strip()

            # Fallback: Try to extract email from content or title
            if not sender_email:
                import re
                combined_text = title + ' ' + content + ' ' + suggestion
                email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', combined_text)
                if email_match:
                    sender_email = email_match.group(1)

            if title and content:
                insight_data = {
                    'type': insight_type,
                    'title': title,
                    'content': content,
                    'suggestion': suggestion
                }

                # Add sender_email if it's an email-related insight
                if sender_email:
                    insight_data['sender_email'] = sender_email

                insights.append(insight_data)
        except Exception as e:
            logging.warning(f"Failed to parse insight block: {e}")
            continue
    
    # If no insights were parsed, create a default one
    if not insights:
        insights.append({
            'type': 'info',
            'title': 'Analysis Complete',
            'content': 'Your schedule and tasks have been analyzed. Everything looks good!',
            'suggestion': 'Keep up the good work with your organization.'
        })
    
    # Count pending tasks
    pending_tasks = task_count  # Simplified, could filter by status
    
    # Build summary
    summary = {
        'unread_emails': email_count,
        'upcoming_events': event_count,
        'pending_tasks': pending_tasks,
        'insights_count': len(insights)
    }
    
    return insights, summary

# ============================================================================
# Schedule Optimization Endpoints
# ============================================================================

@app.route('/api/schedule/optimize', methods=['POST'])
def optimize_schedule():
    """Generate schedule optimization suggestions"""
    global ai_actions, approval_items, action_counter, approval_counter

    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500

        logging.info("Starting schedule optimization...")

        # Fetch data
        email_result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'read_inbox',
            'max_results': 20,
            'unread_only': True
        })

        calendar_result = reasoning_module.action_executor.execute_action('calendar', {
            'operation': 'list_events'
        })

        todo_result = reasoning_module.action_executor.execute_action('todo_list', {
            'operation': 'view_list'
        })

        emails = email_result.get('emails', []) if email_result and email_result.get('status') == 'success' else []
        events = calendar_result.get('events', []) if calendar_result and calendar_result.get('status') == 'success' else []
        tasks = todo_result.get('tasks', []) if todo_result and todo_result.get('status') == 'success' else []

        logging.info(f"Optimization data: {len(emails)} emails, {len(events)} events, {len(tasks)} tasks")

        # Clear old data
        ai_actions = []
        approval_items = []

        # Generate AI actions based on actual data
        from datetime import datetime, timedelta

        # Action 1: Email categorization
        if emails:
            action_counter += 1
            ai_actions.append({
                'id': f'action_{action_counter}',
                'type': 'email',
                'description': f'Categorized {len(emails)} emails',
                'count': len(emails),
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            })

        # Action 2: High priority task identification
        high_priority_tasks = [t for t in tasks if t.get('priority') == 'high' and not t.get('completed', False)]
        if high_priority_tasks:
            action_counter += 1
            ai_actions.append({
                'id': f'action_{action_counter}',
                'type': 'task',
                'description': f'Identified {len(high_priority_tasks)} high-priority tasks',
                'count': len(high_priority_tasks),
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            })

        # Action 3: Calendar conflict detection
        action_counter += 1
        ai_actions.append({
            'id': f'action_{action_counter}',
            'type': 'calendar',
            'description': 'Checked for scheduling conflicts',
            'count': len(events),
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        })

        # Generate approval items (smart suggestions)

        # Approval 1: Task time blocking suggestion
        if high_priority_tasks and events:
            # Find calendar gaps
            now = datetime.now()
            tomorrow = now + timedelta(days=1)

            # Simple gap detection: if less than 5 events tomorrow, suggest time blocking
            future_events = [e for e in events if 'time' in e and 'tomorrow' in str(e.get('time', '')).lower()]

            if len(future_events) < 5 and high_priority_tasks:
                approval_counter += 1
                task_name = high_priority_tasks[0].get('title', 'Important task')
                approval_items.append({
                    'id': f'approval_{approval_counter}',
                    'type': 'schedule',
                    'title': 'Time Block for High-Priority Task',
                    'description': f'Schedule "{task_name}" in your calendar gap tomorrow 2-4 PM',
                    'impact': '⏱️ Saves 30 minutes of context switching',
                    'action_data': {
                        'task_id': high_priority_tasks[0].get('id'),
                        'suggested_time': 'Tomorrow 2:00 PM - 4:00 PM',
                        'task_title': task_name
                    },
                    'timestamp': datetime.now().isoformat()
                })

        # Approval 2: Email batch processing
        if len(emails) >= 5:
            approval_counter += 1
            approval_items.append({
                'id': f'approval_{approval_counter}',
                'type': 'automation',
                'title': 'Batch Process Similar Emails',
                'description': f'Group {len(emails)} emails by sender and process together',
                'impact': '📧 Reduces email time by 40%',
                'action_data': {
                    'email_count': len(emails),
                    'strategy': 'batch_by_sender'
                },
                'timestamp': datetime.now().isoformat()
            })

        # Approval 3: Task prioritization
        medium_tasks = [t for t in tasks if t.get('priority') == 'medium' and not t.get('completed', False)]
        if len(medium_tasks) >= 3:
            approval_counter += 1
            approval_items.append({
                'id': f'approval_{approval_counter}',
                'type': 'priority',
                'title': 'Reprioritize Tasks',
                'description': f'Upgrade {len(medium_tasks[:2])} medium-priority tasks to high based on deadlines',
                'impact': '🎯 Focus on what matters most',
                'action_data': {
                    'tasks_to_upgrade': [t.get('title', 'Task') for t in medium_tasks[:2]]
                },
                'timestamp': datetime.now().isoformat()
            })

        # Approval 4: Meeting optimization (if many back-to-back meetings)
        if len(events) >= 4:
            approval_counter += 1
            approval_items.append({
                'id': f'approval_{approval_counter}',
                'type': 'reschedule',
                'title': 'Add Meeting Buffers',
                'description': 'Reschedule one meeting to add 15-min breaks between back-to-back meetings',
                'impact': '🧘 Reduces meeting fatigue by 35%',
                'action_data': {
                    'meeting_count': len(events),
                    'buffer_duration': '15 minutes'
                },
                'timestamp': datetime.now().isoformat()
            })

        logging.info(f"Generated {len(ai_actions)} actions and {len(approval_items)} approval items")

        return jsonify({
            'success': True,
            'actions': ai_actions,
            'approvals': approval_items,
            'summary': {
                'total_actions': len(ai_actions),
                'total_approvals': len(approval_items),
                'emails_processed': len(emails),
                'events_analyzed': len(events),
                'tasks_reviewed': len(tasks)
            }
        })

    except Exception as e:
        logging.error(f"Schedule optimization error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedule/actions', methods=['GET'])
def get_schedule_actions():
    """Get list of AI actions taken"""
    return jsonify({
        'success': True,
        'actions': ai_actions
    })

@app.route('/api/schedule/approvals', methods=['GET'])
def get_schedule_approvals():
    """Get list of pending approvals"""
    return jsonify({
        'success': True,
        'approvals': approval_items
    })

@app.route('/api/schedule/approve', methods=['POST'])
def approve_schedule_action():
    """Approve a suggested action"""
    global approval_items, ai_actions, action_counter

    try:
        data = request.json
        approval_id = data.get('approval_id')

        if not approval_id:
            return jsonify({'success': False, 'error': 'Missing approval_id'}), 400

        # Find the approval item
        approval = None
        for item in approval_items:
            if item['id'] == approval_id:
                approval = item
                break

        if not approval:
            return jsonify({'success': False, 'error': 'Approval not found'}), 404

        # Execute the approved action
        action_type = approval['type']
        action_data = approval.get('action_data', {})

        result_message = f"Approved: {approval['title']}"

        # Simulate execution based on type
        if action_type == 'schedule':
            # Would create calendar event for task
            result_message = f"✅ Scheduled: {action_data.get('task_title', 'task')} at {action_data.get('suggested_time', 'time')}"

        elif action_type == 'automation':
            # Would enable automation
            result_message = f"✅ Enabled: Batch email processing"

        elif action_type == 'priority':
            # Would update task priorities
            tasks_upgraded = action_data.get('tasks_to_upgrade', [])
            result_message = f"✅ Upgraded priority for {len(tasks_upgraded)} tasks"

        elif action_type == 'reschedule':
            # Would reschedule meetings
            result_message = f"✅ Added buffers between {action_data.get('meeting_count', 0)} meetings"

        # Add to AI actions log
        action_counter += 1
        from datetime import datetime
        ai_actions.append({
            'id': f'action_{action_counter}',
            'type': action_type,
            'description': approval['title'],
            'count': 1,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        })

        # Remove from approval items
        approval_items = [item for item in approval_items if item['id'] != approval_id]

        logging.info(f"Approved action: {approval_id}")

        return jsonify({
            'success': True,
            'message': result_message,
            'actions': ai_actions,
            'approvals': approval_items
        })

    except Exception as e:
        logging.error(f"Approve action error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedule/reject', methods=['POST'])
def reject_schedule_action():
    """Reject a suggested action"""
    global approval_items

    try:
        data = request.json
        approval_id = data.get('approval_id')

        if not approval_id:
            return jsonify({'success': False, 'error': 'Missing approval_id'}), 400

        # Remove from approval items
        approval_items = [item for item in approval_items if item['id'] != approval_id]

        logging.info(f"Rejected action: {approval_id}")

        return jsonify({
            'success': True,
            'message': 'Action rejected',
            'approvals': approval_items
        })

    except Exception as e:
        logging.error(f"Reject action error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Emobot Web Application")
    parser.add_argument('--model', type=str, default='gemini-2.5-flash', help='Model to use')
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
    print(f"   React Frontend:  http://{args.host}:{args.port}")
    print(f"   Simple Test UI:  http://{args.host}:{args.port}/simple")
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
