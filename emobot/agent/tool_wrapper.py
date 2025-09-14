from smolagents import Tool
from typing import Dict, Any

class MCPToolWrapper(Tool):
    """Wrapper for MCP tools to work with smolagents"""
    
    def __init__(self, action_executor, tool_name: str):
        super().__init__()
        self.action_executor = action_executor
        self.tool_name = tool_name
        self.name = tool_name
        self.description = f"MCP tool wrapper for {tool_name}"
        self.output_type = "string"
        # Define inputs to be compatible with smolagents
        self.inputs = {
            "parameters": {
                "type": "object",
                "description": "Tool parameters",
                "nullable": True
            }
        }
    
    def forward(self, parameters: Dict[str, Any] = None) -> str:
        """Execute the MCP tool"""
        try:
            if parameters is None:
                parameters = {}
                
            result = self.action_executor.execute_action(self.tool_name, parameters)
            
            if result.get("status") == "error":
                raise Exception(result.get("error_message", "Unknown error"))
            
            # Return the result content, not the entire result object
            if "result" in result:
                return str(result["result"])
            elif "data" in result:
                return str(result["data"])
            elif "results" in result:
                return str(result["results"])
            elif "formatted_results" in result:
                return str(result["formatted_results"])
            else:
                return str(result)
                
        except Exception as e:
            return f"Tool execution failed: {str(e)}" 