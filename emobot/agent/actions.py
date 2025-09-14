import requests
import json
from typing import Dict, Any, List, Optional, Callable
import markdownify
import time
from datetime import datetime
import logging

class ActionExecutor:
    """
    Action Execution Module: Executes tool calls through MCP server
    
    Manages communication with MCP tool server and handles tool execution results.
    """

    def __init__(self, server_url: str = "http://127.0.0.1:8080"):
        """
        Initialize action executor

        Args:
            server_url: MCP tool server URL
        """
        self.server_url = server_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Execution statistics
        self.execution_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "tool_stats": {},
            "response_times": []
        }
        
        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test connection to MCP server"""
        try:
            response = self.session.get(f"{self.server_url}/tools")
            if response.status_code == 200:
                self.logger.info(f"Successfully connected to MCP server: {self.server_url}")
            else:
                self.logger.warning(f"MCP server returned status {response.status_code}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from MCP server"""
        try:
            response = self.session.get(f"{self.server_url}/tools")
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get tools: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting tools: {e}")
            return []

    def execute_action(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool action

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters

        Returns:
            Execution result
        """
        start_time = time.time()
        self.execution_stats["total_calls"] += 1
        
        try:
            # Prepare request
            request_data = {
                "tool_name": tool_name,
                "parameters": parameters
            }
            
            # Execute tool
            response = self.session.post(
                f"{self.server_url}/execute",
                json=request_data,
                timeout=30
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            self.execution_stats["response_times"].append(response_time)
            
            if response.status_code == 200:
                result = response.json()
                self.execution_stats["successful_calls"] += 1
                
                # Update tool statistics
                if tool_name not in self.execution_stats["tool_stats"]:
                    self.execution_stats["tool_stats"][tool_name] = {
                        "calls": 0,
                        "successes": 0,
                        "average_time": 0
                    }
                
                tool_stats = self.execution_stats["tool_stats"][tool_name]
                tool_stats["calls"] += 1
                tool_stats["successes"] += 1
                tool_stats["average_time"] = (
                    (tool_stats["average_time"] * (tool_stats["calls"] - 1) + response_time) 
                    / tool_stats["calls"]
                )
                
                return result
            else:
                error_msg = f"Tool execution failed with status {response.status_code}"
                self.execution_stats["failed_calls"] += 1
                return {
                    "status": "error",
                    "error_message": error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = "Tool execution timed out"
            self.execution_stats["failed_calls"] += 1
            return {
                "status": "error",
                "error_message": error_msg
            }
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            self.execution_stats["failed_calls"] += 1
            return {
                "status": "error",
                "error_message": error_msg
            }

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_calls = self.execution_stats["total_calls"]
        successful_calls = self.execution_stats["successful_calls"]
        
        # Calculate success rate
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Calculate average response time
        response_times = self.execution_stats["response_times"]
        average_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Find most used tool
        most_used_tool = None
        if self.execution_stats["tool_stats"]:
            most_used_tool = max(
                self.execution_stats["tool_stats"].items(),
                key=lambda x: x[1]["calls"]
            )[0]
        
        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": self.execution_stats["failed_calls"],
            "success_rate": success_rate,
            "average_response_time": average_response_time,
            "most_used_tool": most_used_tool,
            "tool_stats": self.execution_stats["tool_stats"]
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on MCP server"""
        try:
            # Test server reachability
            response = self.session.get(f"{self.server_url}/tools", timeout=5)
            server_reachable = response.status_code == 200
            
            # Get available tools
            available_tools = []
            if server_reachable:
                available_tools = response.json()
            
            return {
                "status": "healthy" if server_reachable else "unhealthy",
                "server_url": self.server_url,
                "server_reachable": server_reachable,
                "available_tools": available_tools,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "server_url": self.server_url,
                "server_reachable": False,
                "available_tools": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            } 