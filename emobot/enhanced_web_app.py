"""
Enhanced Web Application for Complex Frontend Integration
Supports React/Vue frontend with comprehensive API endpoints
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import time
import uuid

# Try to import CORS, make it optional
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("⚠️  flask-cors not installed. CORS will not be enabled.")
    print("   Install with: pip install flask-cors")

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
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Enable CORS if available
if CORS_AVAILABLE:
    CORS(app, origins=['http://localhost:3000', 'http://localhost:8080', 'http://127.0.0.1:3000'])
    print("✅ CORS enabled for frontend development")

# Initialize SocketIO for real-time features
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
reasoning_module = None
reasoning_wrapper = None
mcp_server_thread = None
server_url = "http://127.0.0.1:8080"
active_sessions = {}  # Track active chat sessions

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

# ============================================================================
# CHAT API ENDPOINTS
# ============================================================================

@app.route('/api/chat/message', methods=['POST'])
def send_message():
    """Send a message to the agent"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({'success': False, 'error': 'Empty message'}), 400
        
        if not reasoning_wrapper:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Process query through reasoning wrapper
        result = reasoning_wrapper.process_query_with_steps(message)
        
        # Store in session if needed
        if session_id not in active_sessions:
            active_sessions[session_id] = []
        
        active_sessions[session_id].append({
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'bot_response': result['response'],
            'reasoning_steps': result.get('reasoning_steps', [])
        })
        
        # Emit to WebSocket if connected
        socketio.emit('new_message', {
            'session_id': session_id,
            'message': result['response'],
            'type': 'bot'
        }, room=session_id)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Chat message error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f'Error: {str(e)}'
        }), 500

@app.route('/api/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        history = active_sessions.get(session_id, [])
        return jsonify({
            'success': True,
            'history': history,
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Get all active chat sessions"""
    try:
        sessions = []
        for session_id, history in active_sessions.items():
            if history:
                sessions.append({
                    'session_id': session_id,
                    'last_message': history[-1]['timestamp'],
                    'message_count': len(history)
                })
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# AGENT STATUS & MANAGEMENT API
# ============================================================================

@app.route('/api/agent/status', methods=['GET'])
def get_agent_status():
    """Get comprehensive agent status"""
    try:
        if not reasoning_module:
            return jsonify({
                'success': False,
                'status': 'not_initialized',
                'error': 'Agent not initialized'
            }), 500
        
        # Get various stats
        memory_stats = reasoning_module.memory.get_memory_stats()
        execution_stats = reasoning_module.action_executor.get_execution_stats()
        health = reasoning_module.action_executor.health_check()
        
        return jsonify({
            'success': True,
            'status': 'active',
            'model_id': reasoning_module.model_manager.current_model,
            'server_url': server_url,
            'memory_stats': memory_stats,
            'execution_stats': execution_stats,
            'health': health,
            'active_sessions': len(active_sessions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/agent/memory/clear', methods=['POST'])
def clear_agent_memory():
    """Clear agent memory"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json or {}
        memory_type = data.get('type', 'short_term')  # short_term, working, all
        
        if memory_type == 'short_term':
            reasoning_module.memory.clear_short_term()
        elif memory_type == 'working':
            reasoning_module.memory.working_memory.clear()
        elif memory_type == 'all':
            reasoning_module.memory.clear_short_term()
            reasoning_module.memory.working_memory.clear()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {memory_type} memory',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agent/reflection', methods=['POST'])
def trigger_agent_reflection():
    """Trigger agent self-reflection"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        reflection = reasoning_module.reflect_on_performance()
        
        return jsonify({
            'success': True,
            'reflection': reflection,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# DATA API ENDPOINTS
# ============================================================================

@app.route('/api/data/analytics', methods=['GET'])
def get_analytics_data():
    """Get analytics data for dashboard"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Collect various metrics
        memory_stats = reasoning_module.memory.get_memory_stats()
        execution_stats = reasoning_module.action_executor.get_execution_stats()
        user_prefs = reasoning_module.memory.get_user_preferences()
        
        # Calculate additional metrics
        total_interactions = sum(len(history) for history in active_sessions.values())
        
        analytics = {
            'overview': {
                'total_interactions': total_interactions,
                'active_sessions': len(active_sessions),
                'total_tool_calls': execution_stats['total_calls'],
                'success_rate': execution_stats['success_rate']
            },
            'memory': {
                'short_term_entries': memory_stats['short_term_size'],
                'episodic_entries': memory_stats['episodic_count'],
                'semantic_categories': len(memory_stats['semantic_categories'])
            },
            'tools': {
                'most_used': execution_stats.get('most_used_tool', 'None'),
                'tool_stats': execution_stats.get('tool_stats', {})
            },
            'user_patterns': {
                'most_used_intents': user_prefs.get('most_used_intents', []),
                'active_hours': user_prefs.get('active_hours', []),
                'preferences': user_prefs.get('preferences', {})
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data/export', methods=['GET'])
def export_data():
    """Export agent data"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        export_type = request.args.get('type', 'all')  # memory, sessions, analytics, all
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'export_type': export_type
        }
        
        if export_type in ['memory', 'all']:
            export_data['memory'] = reasoning_module.memory.get_memory_stats()
        
        if export_type in ['sessions', 'all']:
            export_data['sessions'] = active_sessions
        
        if export_type in ['analytics', 'all']:
            export_data['analytics'] = reasoning_module.action_executor.get_execution_stats()
        
        return jsonify({
            'success': True,
            'data': export_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# TOOLS API ENDPOINTS
# ============================================================================

@app.route('/api/tools/list', methods=['GET'])
def list_tools():
    """Get available tools with detailed info"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        tools = reasoning_module.action_executor.get_available_tools()
        execution_stats = reasoning_module.action_executor.get_execution_stats()
        
        # Enhance tools with usage statistics
        enhanced_tools = []
        for tool in tools:
            tool_name = tool['name']
            tool_stats = execution_stats.get('tool_stats', {}).get(tool_name, {})
            
            enhanced_tool = {
                **tool,
                'usage_stats': {
                    'calls': tool_stats.get('calls', 0),
                    'successes': tool_stats.get('successes', 0),
                    'average_time': tool_stats.get('average_time', 0),
                    'success_rate': (tool_stats.get('successes', 0) / max(tool_stats.get('calls', 1), 1)) * 100
                }
            }
            enhanced_tools.append(enhanced_tool)
        
        return jsonify({
            'success': True,
            'tools': enhanced_tools,
            'total_tools': len(enhanced_tools)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tools/execute', methods=['POST'])
def execute_tool():
    """Execute a specific tool"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        tool_name = data.get('tool_name')
        parameters = data.get('parameters', {})
        
        if not tool_name:
            return jsonify({'success': False, 'error': 'Tool name required'}), 400
        
        result = reasoning_module.action_executor.execute_tool(tool_name, parameters)
        
        return jsonify({
            'success': True,
            'tool_name': tool_name,
            'parameters': parameters,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tool_name': data.get('tool_name', 'unknown')
        }), 500

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Emobot server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_session')
def handle_join_session(data):
    """Join a chat session room"""
    session_id = data.get('session_id', 'default')
    join_room(session_id)
    emit('joined_session', {'session_id': session_id})

@socketio.on('leave_session')
def handle_leave_session(data):
    """Leave a chat session room"""
    session_id = data.get('session_id', 'default')
    leave_room(session_id)
    emit('left_session', {'session_id': session_id})

@socketio.on('agent_status_request')
def handle_status_request():
    """Handle real-time status request"""
    try:
        if reasoning_module:
            health = reasoning_module.action_executor.health_check()
            emit('agent_status', {
                'status': health['status'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            emit('agent_status', {
                'status': 'not_initialized',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        emit('agent_status', {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

# ============================================================================
# HEALTH & UTILITY ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Comprehensive health check"""
    try:
        health_data = {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'agent_initialized': reasoning_module is not None,
            'mcp_server': server_url,
            'active_sessions': len(active_sessions),
            'cors_enabled': CORS_AVAILABLE
        }
        
        if reasoning_module:
            agent_health = reasoning_module.action_executor.health_check()
            health_data['agent_health'] = agent_health
        
        return jsonify(health_data)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get frontend configuration"""
    return jsonify({
        'success': True,
        'config': {
            'api_base_url': request.host_url.rstrip('/'),
            'websocket_url': request.host_url.rstrip('/'),
            'features': {
                'chat': True,
                'analytics': True,
                'tools': True,
                'real_time': True,
                'export': True
            },
            'limits': {
                'max_message_length': 4000,
                'max_sessions': 100,
                'session_timeout': 3600
            }
        }
    })

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Emobot Web Application")
    parser.add_argument('--model', type=str, default='gemini-2.0-flash', help='Model to use')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 Starting Enhanced Emobot Web Application")
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
    print(f"✅ Enhanced Emobot API Server is running!")
    print(f"🌐 API Base URL: http://{args.host}:{args.port}")
    print(f"📡 WebSocket URL: ws://{args.host}:{args.port}")
    print(f"🔧 MCP Server: {server_url}")
    print("="*60 + "\n")
    
    # Start Flask web server with SocketIO
    socketio.run(
        app,
        host=args.host,
        port=args.port,
        debug=args.debug,
        allow_unsafe_werkzeug=True
    )

if __name__ == '__main__':
    main()
