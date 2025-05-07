"""
Agents package for the emobot assistant.
Contains specialized agents for different tasks.
"""

# emobot/agents/__init__.py
from emobot.agents.research_agent import ResearchAgent
from emobot.agents.email_agent import EmailAgent
# Import any other agents you've implemented

__all__ = ['ResearchAgent', 'EmailAgent']