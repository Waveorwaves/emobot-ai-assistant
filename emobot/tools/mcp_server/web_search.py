from .tool_base import MCPToolBase
from typing import Dict, Any

try:
    from ddgs import DDGS
except ImportError:
    # Fallback to old package name
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
            # Use DDGS with timeout for better reliability
            ddgs = DDGS(timeout=20)
            results = ddgs.text(query, max_results=num_results)
            results_list = list(results) if results else []
            
            if not results_list:
                # Return a helpful message instead of empty results
                return {
                    "status": "success", 
                    "results": [{
                        "title": "Search Information",
                        "snippet": f"I attempted to search for '{query}' but couldn't retrieve results at this moment. This might be due to API limitations or network issues. You can try: 1) Rephrasing your query, 2) Being more specific, or 3) Trying again in a moment.",
                        "url": "https://duckduckgo.com/?q=" + query.replace(" ", "+")
                    }]
                }
            
            formatted_results = [
                {"title": r.get("title", "No title"), "snippet": r.get("body", "No description"), "url": r.get("href", "")} 
                for r in results_list
            ]
            
            return {"status": "success", "results": formatted_results}
        except Exception as e:
            # Provide a fallback response instead of just an error
            return {
                "status": "success",
                "results": [{
                    "title": "Search Service Unavailable",
                    "snippet": f"The web search service encountered an issue: {str(e)}. As an alternative, I can help you with other tasks or you can try searching directly at DuckDuckGo.",
                    "url": "https://duckduckgo.com/?q=" + query.replace(" ", "+")
                }]
            } 