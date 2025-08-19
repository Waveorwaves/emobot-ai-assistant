from smolagents import Tool
from typing import Dict, Any

class MCPToolWrapper(Tool):
    """Wrapper for MCP tools to work with smolagents"""
    
    def __init__(self, action_executor):
        super().__init__()
        self.action_executor = action_executor
        self.name = "mcp_tool"
        self.description = "MCP tool wrapper"
        self.output_type = "string"
        self.inputs = {}
    
    def forward(self, **kwargs) -> str:
        """Execute the MCP tool"""
        try:
            result = self.action_executor.execute_action(self.name, kwargs)
            
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