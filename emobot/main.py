import argparse
import threading
import time
import yaml
import os
import sys
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from agent.reasoning import ReasoningModule
from agent.perception import PerceptionModule
from tools.mcp_server.server import MCPToolServer

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class EmobotApp:
    """
    Emobot Application Main Class
    
    Manages agent lifecycle, user interaction, and system functionality
    """
    
    def __init__(self, model_id: str = "gemini-1.5-flash", config_path: str = "configs/mcp.yaml"):
        # 如果没有指定模型，尝试从环境变量获取
        if model_id is None:
            model_id = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
        self.model_id = model_id or "gemini-1.5-flash"  # 确保不为 None
        self.config_path = config_path
        self.agent: Optional[ReasoningModule] = None
        self.server_thread: Optional[threading.Thread] = None
        self.server_url: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        
        # Interactive commands
        self.commands = {
            "/help": self._show_help,
            "/stats": self._show_stats,
            "/memory": self._show_memory,
            "/clear": self._clear_memory,
            "/tools": self._list_tools,
            "/health": self._health_check,
            "/explain": self._explain_last,
            "/preferences": self._show_preferences,
            "/reflect": self._reflect,
            "/pending": self._show_pending_confirmation,
            "/cancel": self._cancel_pending_confirmation,
            "/test_email": self._test_email_generation,
            "/exit": self._exit
        }
        
        self.last_query = None
        self.last_response = None
    


    def start(self):
        """Start Emobot application"""
        self.logger.info("Starting Emobot...")
        
        # Start MCP tool server
        if not self._start_mcp_server():
            self.logger.error("Failed to start MCP server")
            return
        
        # Initialize agent
        if not self._initialize_agent():
            self.logger.error("Failed to initialize agent")
            return
        
        # Show welcome message
        self._show_welcome()
        
        # Main interaction loop
        self._run_interaction_loop()

    def _start_mcp_server(self) -> bool:
        """Start MCP tool server"""
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
            
            server_config = config.get("server", {})
            host = server_config.get("host", "127.0.0.1")
            port = server_config.get("port", 8080)
            self.server_url = f"http://{host}:{port}"
            
            # Start server in background thread
            self.server_thread = threading.Thread(
                target=self._run_mcp_server,
                args=(self.config_path,),
                daemon=True
            )
            self.server_thread.start()
            
            # Wait for server to start
            time.sleep(2)
            
            self.logger.info(f"MCP server started at {self.server_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            return False

    def _run_mcp_server(self, config_path: str):
        """Run MCP server"""
        try:
            server = MCPToolServer(config_path)
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            server_config = config.get("server", {})
        
            server.app.run(
                host=server_config.get("host", "127.0.0.1"),
                port=server_config.get("port", 8080),
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            self.logger.error(f"MCP server runtime error: {e}")

    def _initialize_agent(self) -> bool:
        """Initialize agent"""
        try:
            # Remove API key check, let ModelManager handle it automatically
            # ModelManager will automatically check API keys and select appropriate models
            
            # Ensure server_url is set
            if not self.server_url:
                self.server_url = "http://127.0.0.1:8080"
            
            self.agent = ReasoningModule(
                model_id=self.model_id,
                server_url=self.server_url,
                # system_prompt_path="configs/system_prompt.md",
                use_local_model=False
            )
            
            self.logger.info(f"Agent initialized successfully (model: {self.model_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}")
            return False

    def _show_welcome(self):
        """Show welcome message"""
        print("\n" + "="*60)
        print("🤖 Welcome to Emobot - Your Intelligent Assistant")
        print("="*60)
        print(f"📌 Model: {self.model_id}")
        print(f"🔧 Tool Server: {self.server_url}")
        print("💡 Type /help to see available commands")
        print("📝 Type your questions directly to start conversation")
        print("="*60 + "\n")

    def _run_interaction_loop(self):
        """Run main interaction loop"""
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You > ").strip()
                
                if not user_input:
                    continue
                
                # Check if it's a command
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                else:
                    # Handle regular queries
                    self._handle_query(user_input)
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                self.logger.error(f"Interaction loop error: {e}")
                print(f"❌ Error occurred: {e}")

    def _handle_command(self, command: str):
        """Handle system commands"""
        cmd_parts = command.split()
        base_cmd = cmd_parts[0].lower()
        
        if base_cmd in self.commands:
            self.commands[base_cmd]()
        else:
            print(f"❓ Unknown command: {base_cmd}")
            print("💡 Type /help to see available commands")

    def _handle_query(self, query: str):
        """Handle user queries with confirmation support"""
        print("\n🤔 Thinking...")
        
        start_time = time.time()
        
        try:
            # Ensure agent is initialized
            if not self.agent:
                print("❌ Agent not initialized, please check configuration")
                return
            
            # Check if there's a pending confirmation
            if self.agent.has_pending_confirmation():
                print("🔄 Processing confirmation response...")
                response = self.agent.handle_confirmation_response(query)
            else:
                # Call agent to process query
                response = self.agent.process_query(query)
            
            # Record query and response
            self.last_query = query
            self.last_response = response
            
            # Display response
            elapsed_time = time.time() - start_time
            print(f"\n🤖 Emobot ({elapsed_time:.2f}s):")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
        except Exception as e:
            self.logger.error(f"Failed to process query: {e}")
            print(f"❌ Error processing query: {e}")

    # ========== Command Handler Functions ==========
    
    def _show_help(self):
        """Show help information"""
        help_text = """
📚 Available Commands:

  /help         - Show this help information
  /stats        - Show execution statistics
  /memory       - Show memory system status
  /clear        - Clear short-term memory
  /tools        - List available tools
  /health       - Check system health status
  /explain      - Explain reasoning process of last query
  /preferences  - Show user preference analysis
  /reflect      - Let agent reflect on its performance
  /pending      - Show pending confirmation requests
  /cancel       - Cancel pending confirmation requests
  /test_email   - Test email content generation
  /exit         - Exit program

💡 Tips:
  - Type questions directly to chat with Emobot
  - Supports mixed English and Chinese input
  - Can request to search information, manage emails and to-do items
  - Some operations (like sending emails) require confirmation for security
  - When prompted for confirmation, type 'yes' or 'y' to proceed, 'no' or 'n' to cancel
  - Use /pending to see what actions are waiting for confirmation
  - Use /cancel to cancel pending confirmations
"""
        print(help_text)

    def _show_stats(self):
        """Show execution statistics"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        stats = self.agent.action_executor.get_execution_stats()
        
        print("\n📊 Execution Statistics:")
        print(f"  Total Calls: {stats['total_calls']}")
        print(f"  Successful: {stats['successful_calls']}")
        print(f"  Failed: {stats['failed_calls']}")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        print(f"  Average Response Time: {stats['average_response_time']:.2f}s")
        
        if stats['most_used_tool']:
            print(f"  Most Used Tool: {stats['most_used_tool']}")
        
        if stats['tool_stats']:
            print("\n  Tool Usage Details:")
            for tool, tool_stats in stats['tool_stats'].items():
                print(f"    {tool}:")
                print(f"      Calls: {tool_stats['calls']} times")
                print(f"      Successes: {tool_stats['successes']} times")
                print(f"      Average Time: {tool_stats['average_time']:.2f}s")

    def _show_memory(self):
        """Show memory system status"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        memory_stats = self.agent.memory.get_memory_stats()
        
        print("\n🧠 Memory System Status:")
        print(f"  Short-term Memory Entries: {memory_stats['short_term_size']}")
        print(f"  Working Memory Keys: {', '.join(memory_stats['working_memory_keys']) or 'None'}")
        print(f"  Episodic Memory Entries: {memory_stats['episodic_count']}")
        print(f"  Semantic Memory Categories: {', '.join(memory_stats['semantic_categories'])}")
        print(f"\n  User Interaction Statistics:")
        print(f"    Total Interactions: {memory_stats['user_patterns']['total_interactions']}")
        print(f"    Unique Intents: {memory_stats['user_patterns']['unique_intents']}")
        print(f"    Tools Used: {memory_stats['user_patterns']['unique_tools']}")

    def _clear_memory(self):
        """Clear short-term memory"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        self.agent.memory.clear_short_term()
        print("✅ Short-term memory cleared")

    def _list_tools(self):
        """List available tools"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        tools = self.agent.action_executor.get_available_tools()
        
        if not tools:
            print("❌ No tools available")
            return
        
        print("\n🔧 Available Tools:")
        for tool in tools:
            print(f"\n  📌 {tool['name']}")
            print(f"     {tool['description']}")
            
            params = tool.get('parameters', {}).get('properties', {})
            if params:
                print("     Parameters:")
                for param, info in params.items():
                    required = param in tool.get('parameters', {}).get('required', [])
                    req_mark = " (Required)" if required else ""
                    print(f"       - {param}: {info.get('description', 'N/A')}{req_mark}")

    def _health_check(self):
        """Perform health check"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        health = self.agent.action_executor.health_check()
        
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌"
        }
        
        print("\n🏥 System Health Status:")
        print(f"  Status: {status_emoji.get(health['status'], '❓')} {health['status']}")
        print(f"  Server: {health['server_url']}")
        print(f"  Reachable: {'Yes' if health['server_reachable'] else 'No'}")
        print(f"  Available Tools: {len(health['available_tools'])}")
        print(f"  Check Time: {health['timestamp']}")
        
        if 'error' in health:
            print(f"  Error: {health['error']}")

    def _explain_last(self):
        """Explain reasoning process of last query"""
        if not self.last_query:
            print("❌ No previous query record")
            return
        
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        print(f"\n🔍 Explaining query: '{self.last_query}'")
        explanation = self.agent.explain_reasoning(self.last_query)
        print(explanation)

    def _show_preferences(self):
        """Show user preference analysis"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        prefs = self.agent.memory.get_user_preferences()
        
        print("\n👤 User Preference Analysis:")
        
        if prefs['most_used_intents']:
            print("\n  Most Used Intents:")
            for intent, count in prefs['most_used_intents']:
                print(f"    - {intent}: {count} times")
        
        if prefs['most_used_tools']:
            print("\n  Most Used Tools:")
            for tool, count in prefs['most_used_tools']:
                print(f"    - {tool}: {count} times")
        
        if prefs['active_hours']:
            print(f"\n  Active Hours: {', '.join([f'{h}:00' for h in prefs['active_hours']])}")
        
        if prefs['preferences']:
            print("\n  Preferences:")
            for key, value in prefs['preferences'].items():
                print(f"    - {key}: {value}")

    def _reflect(self):
        """Let agent reflect on its performance"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        print("\n🤔 Reflecting...")
        reflection = self.agent.reflect_on_performance()
        
        print("\n📝 Performance Reflection Report:")
        print(f"\n  Interaction Count: {reflection['interaction_count']}")
        
        print("\n  Tool Effectiveness Assessment:")
        for tool, effectiveness in reflection['tool_effectiveness'].items():
            print(f"    - {tool}: {effectiveness*100:.0f}%")
        
        print("\n  User Satisfaction Indicators:")
        for indicator, value in reflection['user_satisfaction_indicators'].items():
            if isinstance(value, float):
                print(f"    - {indicator}: {value*100:.0f}%")
            else:
                print(f"    - {indicator}: {value}")
        
        print("\n  Improvement Suggestions:")
        for suggestion in reflection['improvement_suggestions']:
            print(f"    - {suggestion}")
        
        print("\n  Learning Progress:")
        for metric, value in reflection['learning_progress'].items():
            print(f"    - {metric}: {value}")

    def _show_pending_confirmation(self):
        """Show pending confirmation requests"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        pending_requests = self.agent.get_pending_confirmation_requests()
        
        if not pending_requests:
            print("✅ No pending confirmation requests.")
            return
        
        print("\n⚠️ Pending Confirmation Requests:")
        for req in pending_requests:
            print(f"  - ID: {req['id']}")
            print(f"    Query: {req['query']}")
            print(f"    Status: {req['status']}")
            print(f"    Created At: {req['created_at']}")
            print(f"    Expires At: {req['expires_at']}")
            print("-" * 20)

    def _cancel_pending_confirmation(self):
        """Cancel pending confirmation requests"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        pending_requests = self.agent.get_pending_confirmation_requests()
        
        if not pending_requests:
            print("✅ No pending confirmation requests to cancel.")
            return
        
        print("\n🚫 Cancelling pending confirmation requests...")
        for req in pending_requests:
            print(f"  - Cancelling ID: {req['id']}")
            self.agent.cancel_confirmation_request(req['id'])
            print(f"    Cancelled ID: {req['id']}")
        print("✅ All pending confirmation requests cancelled.")

    def _test_email_generation(self):
        """Test email generation"""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        print("\n💌 Testing Email Generation...")
        
        test_queries = [
            "Send a test email to john.doe@example.com",
            "Send an email to Wang_Yifei1213@outlook.com to ask if he has finished the task",
            "Email alice@company.com to ask about the meeting reschedule",
            "Send bob@email.com a message to inform him about the project update"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📧 Test {i}: {query}")
            try:
                subject, body = self.agent._extract_email_content(query)
                print(f"   📋 Subject: {subject}")
                print(f"   📝 Body: {body}")
                print("   " + "-" * 40)
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n✅ Email generation test completed!")

    def _exit(self):
        """Exit program"""
        print("\n👋 Thank you for using Emobot, goodbye!")
        sys.exit(0)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Emobot - Intelligent Assistant based on smolagents")
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-1.5-flash",
        help="Language model to use (default: gemini-1.5-flash)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/mcp.yaml",
        help="MCP configuration file path (default: configs/mcp.yaml)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()

    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and start application
    app = EmobotApp(
        model_id=args.model,
        config_path=args.config
        )
    
    try:
        app.start()
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
