import yaml
import importlib
from flask import Flask, request, jsonify
from typing import Dict, Any

class MCPToolServer:
    """
    A server that exposes MCP-compliant tools over an HTTP interface.
    It loads tools dynamically based on a YAML configuration file.
    """

    def __init__(self, config_path: str):
        self.app = Flask(__name__)
        self.config = self._load_config(config_path)
        self.tools = self._load_tools()
        self._register_routes()

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Loads the YAML configuration file."""
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _load_tools(self) -> Dict[str, Any]:
        """Dynamically loads tool classes based on the configuration."""
        loaded_tools = {}
        # Check if demo_mode is enabled globally
        demo_mode = self.config.get("demo_mode", True)  # Default to True for demo
        
        for tool_config in self.config.get("tools", []):
            if tool_config.get("enabled", False):
                try:
                    module_path = tool_config["module"]
                    class_name = tool_config["class"]
                    module = importlib.import_module(module_path)
                    tool_class = getattr(module, class_name)
                    
                    # Pass demo_mode to EmailTool
                    if class_name == "EmailTool":
                        loaded_tools[tool_config["name"]] = tool_class(demo_mode=demo_mode)
                    else:
                        loaded_tools[tool_config["name"]] = tool_class()
                    print(f"Successfully loaded tool: {tool_config['name']}")
                except (ImportError, AttributeError, KeyError) as e:
                    print(f"Error loading tool '{tool_config.get('name', 'N/A')}': {e}")
        return loaded_tools

    def _register_routes(self):
        """Registers the Flask API routes."""
        
        @self.app.route("/tools", methods=["GET"])
        def list_tools():
            """Returns a list of available tools and their schemas."""
            schemas = [tool.get_schema() for tool in self.tools.values()]
            return jsonify(schemas)

        @self.app.route("/execute", methods=["POST"])
        def execute_tool():
            """Executes a tool with the given parameters."""
            data = request.json
            tool_name = data.get("tool_name")
            parameters = data.get("parameters", {})

            if not tool_name or tool_name not in self.tools:
                return jsonify({"status": "error", "error_message": "Tool not found."}), 404

            tool = self.tools[tool_name]
            try:
                result = tool.execute(**parameters)
                return jsonify(result)
            except Exception as e:
                return jsonify({"status": "error", "error_message": str(e)}), 500

    def run(self, host: str, port: int):
        """Starts the Flask server."""
        self.app.run(host=host, port=port)

def start_server():
    """Initializes and starts the MCP Tool Server."""
    config_path = "configs/mcp.yaml"
    config = yaml.safe_load(open(config_path, "r"))
    server_config = config.get("server", {})
    
    server = MCPToolServer(config_path)
    
    host = server_config.get("host", "127.0.0.1")
    port = server_config.get("port", 8080)
    
    print(f"Starting MCP Tool Server at http://{host}:{port}")
    server.run(host=host, port=port)

if __name__ == "__main__":
    start_server() 