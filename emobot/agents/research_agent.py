# emobot/agents/research_agent.py
"""
Research agent for the emobot assistant.
Handles web searches and information gathering.
"""
import logging
from typing import Dict, Any, Optional

from emobot.core.config import logger
from emobot.services.gemini_service import GeminiService

class ResearchAgent:
    """Agent for researching information."""
    
    def __init__(self):
        """Initialize the research agent."""
        self.gemini_service = GeminiService()
        logger.info("Research agent initialized")
    
    async def process(self, message_text: str, message_data: Dict[str, Any]) -> str:
        """Process a research request.
        
        Args:
            message_text: The user message
            message_data: Additional message data
            
        Returns:
            Research response
        """
        # Create a research-specific prompt
        research_prompt = f"""
        You are a research assistant. The user is asking for information about:
        "{message_text}"
        
        Please provide a helpful and accurate response based on your knowledge. Focus on:
        1. Giving factual information
        2. Providing context when needed
        3. Being clear and concise
        
        For financial questions (stocks, prices, markets):
        - Include current price information if asked
        - Mention if the information might be volatile or time-sensitive
        
        For technical questions:
        - Provide step-by-step explanations when helpful
        - Include code examples if relevant
        """
        
        try:
            # Use Gemini to generate the research response
            response = await self.gemini_service.generate_response(research_prompt)
            return response
        except Exception as e:
            logger.error(f"Error in research agent: {e}")
            return f"I tried to research that for you, but encountered an issue. Could you try asking in a different way?"
    
    async def search(self, query: str) -> str:
        """Perform a search for information.
        
        This is a simplified version - in a real implementation,
        this would connect to search APIs, databases, etc.
        
        Args:
            query: The search query
            
        Returns:
            Search results
        """
        search_prompt = f"""
        Provide accurate and helpful information about: "{query}"
        
        Be factual and concise. If this is about current events, stocks, or time-sensitive information,
        note that the information might not be up-to-date.
        """
        
        try:
            return await self.gemini_service.generate_response(search_prompt)
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return "I couldn't find information on that topic."