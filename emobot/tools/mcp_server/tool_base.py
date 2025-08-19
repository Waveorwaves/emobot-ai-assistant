from typing import Dict, Any

class MCPToolBase:
    """
    Base class for all MCP (Model-Centric Protocol) tools.
    """
    
    name: str = "mcp_tool_base"
    description: str = "This is a base class for MCP tools and should not be used directly."
    parameters: Dict[str, Any] = {}

    def __init__(self):
        """
        Initializes the tool. Can be used for loading models or setting up connections.
        """
        pass

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Executes the tool's main logic with the given parameters.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("The 'execute' method must be implemented by the tool subclass.")

    def get_schema(self) -> Dict[str, Any]:
        """
        Returns the tool's schema in a format that language models can understand.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters,
                "required": list(self.parameters.keys()),
            },
        } 