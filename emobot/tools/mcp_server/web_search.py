from .tool_base import MCPToolBase
from typing import Dict, Any
from duckduckgo_search import DDGS

class WebSearchTool(MCPToolBase):
    """
    A tool for performing web searches using the DuckDuckGo search engine.
    """
    
    name: str = "web_search"
    description: str = "Performs a web search for a given query and returns the top results. Useful for finding information on the internet, such as facts, news, or general knowledge."
    parameters: Dict[str, Any] = {
        "query": {
            "type": "string",
            "description": "The search query to be executed."
        },
        "num_results": {
            "type": "integer",
            "description": "The maximum number of search results to return. Defaults to 5."
        }
    }

    def execute(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Executes the web search.

        Args:
            query: The search term.
            num_results: The number of results to return.

        Returns:
            A dictionary containing the search results or an error message.
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
            
            if not results:
                return {"status": "success", "results": "No results found for the query."}
            
            formatted_results = [
                {"title": r.get("title"), "snippet": r.get("body"), "url": r.get("href")} 
                for r in results
            ]
            
            return {"status": "success", "results": formatted_results}
        except Exception as e:
            return {"status": "error", "error_message": f"An error occurred during the web search: {str(e)}"} 