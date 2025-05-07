"""
Main assistant orchestrator for the emobot assistant.
Coordinates between different components to handle user requests.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
import re
from emobot.core.personality import Personality, Emotion
from emobot.core.memory_manager import MemoryManager
from emobot.core.config import logger
from emobot.services.gemini_service import GeminiService
from emobot.agents.research_agent import ResearchAgent
from emobot.agents.email_agent import EmailAgent
from emobot.services.email_service import EmailService

class AssistantAgent:
    """Main orchestrator for the emobot assistant."""
    
    def __init__(self, user_id: str):
        """Initialize the assistant agent for a specific user."""
        self.user_id = user_id
        self.memory = MemoryManager(user_id)
        self.personality = Personality(self.memory.user_preferences)
        self.agents = {}  # Will store agent instances
        self.command_handlers = {}  # Will store command handlers
        
        # Initialize Gemini service
        self.gemini_service = GeminiService()
        
        # Register research agent
        self.register_agent("research", ResearchAgent())

        # Register email agent
        self.register_agent("email", EmailAgent())
        
        # Register basic command handlers
        self._register_default_commands()
        
        logger.info(f"Assistant agent initialized for user {user_id}")
    
    async def process_message(self, message_text: str, message_data: Dict[str, Any] = None) -> str:
        """Process a user message and generate a response."""
        if message_data is None:
            message_data = {}
        
        # Add message to conversation history
        self.memory.add_message("user", message_text)
        
        # Check if this is a command
        if message_text.startswith('/'):
            response = await self._handle_command(message_text, message_data)
        else:
            # Process as a regular message
            response = await self._generate_response(message_text, message_data)
        
        # Add response to conversation history
        self.memory.add_message("assistant", response)
        
        return response
    
    async def _handle_command(self, command_text: str, message_data: Dict[str, Any]) -> str:
        """Handle bot commands (starting with /)."""
        # Extract command and arguments
        parts = command_text.split(maxsplit=1)
        command = parts[0][1:]  # Remove the leading '/'
        args = parts[1] if len(parts) > 1 else ""
        
        # Check if we have a handler for this command
        if command in self.command_handlers:
            try:
                return await self.command_handlers[command](args, message_data)
            except Exception as e:
                logger.error(f"Error handling command {command}: {e}")
                error_response = self.personality.get_error_response()
                return self.personality.format_response(error_response)
        
        # Unknown command
        return f"Unknown command: /{command}. Type /help for available commands."
    
    async def _generate_response(self, message_text: str, message_data: Dict[str, Any]) -> str:
        """Generate a response to a user message."""
        # Debug logging
        logger.info(f"Received message: {message_text}")
        if self._is_task_related(message_text):
            logger.info("Message identified as task-related")
        else:
            logger.info("Message not identified as task-related")

        # Check if this is a task-related query for MCP approach
        if self._is_task_related(message_text):
            try:
                # Handle via MCP approach
                user_id = str(message_data.get("chat", {}).get("id", "default"))
                return await self.gemini_service.handle_task_request(message_text, user_id)
            except Exception as e:
                logger.error(f"Error processing with MCP task handler: {e}")
                # Fall through to regular processing below
        
        # Check if we should handle with intent-specific agent
        intent, confidence = self._analyze_intent(message_text)
        
        # If we have high confidence in the intent and have a registered agent for it
        if confidence > 0.7 and intent in self.agents:
            try:
                return await self.agents[intent].process(message_text, message_data)
            except Exception as e:
                logger.error(f"Error processing with {intent} agent: {e}")
                # Fall back to Gemini
        
        try:
            # Get conversation history
            conversation_history = self.memory.get_conversation_history()
            
            # Create system prompt
            system_prompt = self.gemini_service.create_system_prompt(self.personality.__dict__)
            
            # Full prompt with system instructions
            full_prompt = f"{system_prompt}\n\nUser: {message_text}"
            
            # Generate response using Gemini
            response = await self.gemini_service.generate_contextualized_response(
                full_prompt,
                conversation_history
            )
            
            return response
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {e}")
            
            # Fall back to default keyword-based responses
            if any(word in message_text.lower() for word in ["hello", "hi", "hey"]):
                greeting = self.personality.get_greeting(Emotion.HAPPY)
                return self.personality.format_response(greeting)
            
            # Default acknowledgement
            ack = self.personality.get_acknowledgement(Emotion.THOUGHTFUL)
            return self.personality.format_response(ack) + "\n\nI'm still learning to handle different types of requests."

  
    def _is_task_related(self, message: str) -> bool:
        """More inclusive task detection, but excludes clear email commands."""
        message_lower = message.lower()

        # Keywords that strongly suggest an email-related command
        # Based on your provided email commands:
        # 1. - "Send an email to [email_address] subject [subject_line] body [email_content]"
        # 2. - "Check my unread emails"
        # 3. - "Read my emails"
        email_keywords = [
            "email", "emails", "mail",
            "send to", "recipient", "sender",
            "subject", "body", "content",
            "check my emails", "unread", "read my emails"
        ]
        if any(keyword in message_lower for keyword in email_keywords):
            # If it looks like an email command, it's not a generic task for the MCP approach
            logger.info(f"Message '{message}' identified as email-related by keywords, not a generic task.")
            return False
        
        # Original task detection logic
        action_words = ["add", "put", "create", "show", "list", "mark", "complete", "delete", "remove", "remind", "could", "can", "would"]
        task_words = ["list", "task", "todo", "to-do", "to do", "remember", "remind", "complete", "finish"]
        
        has_action = any(word in message_lower for word in action_words)
        has_task_term = any(word in message_lower for word in task_words)
        
        # If message has both action and task terms, or explicitly mentions "my list"
        is_general_task = (has_action and has_task_term) or "my list" in message_lower
        if is_general_task:
            logger.info(f"Message '{message}' identified as a generic task.")
        return is_general_task

    def _analyze_intent(self, message_text: str) -> Tuple[str, float]:
        """Analyze the intent of a message.
        
        Returns:
            Tuple containing (intent_name, confidence_score)
        """
        # This is a very simple implementation
        # In a real system, this would use NLP techniques or ML models
        
        message_lower = message_text.lower()
        
        if any(word in message_lower for word in ["time", "date", "day"]):
            return "calendar", 0.8
        
        if any(word in message_lower for word in ["search", "find", "look up"]):
            return "research", 0.8
        
        if any(word in message_lower for word in ["remind", "task", "todo"]):
            return "task", 0.8
        
        if any(word in message_lower for word in ["email", "message", "send to", "check my emails"]):
            return "email", 0.8
        
        # Default: uncertain intent
        return "unknown", 0.3
    
    def _register_default_commands(self):
        """Register default command handlers."""
        
        async def help_command(args: str, data: Dict[str, Any]) -> str:
            """Handle the /help command."""
            commands = [
                "/help - Show this help message",
                "/start - Start or restart the bot",
                "/time - Show the current time",
                # Added Email Functionality
                "Email Features:",
                "  - \"Send an email to [email_address] subject [subject_line] body [email_content]\"",
                "  - \"Check my unread emails\"",
                "  - \"Read my emails\"",
            ]
            return "Available commands and features:\n" + "\n".join(commands)
        
        async def start_command(args: str, data: Dict[str, Any]) -> str:
            """Handle the /start command."""
            user_name = data.get("user", {}).get("first_name", "there")
            greeting = self.personality.get_greeting(Emotion.EXCITED)
            greeting_text = self.personality.format_response(greeting)
            
            intro = (
                f"Hi {user_name}! {greeting_text}\n\n"
                "I'm your personal assistant bot. I can help you with:\n"
                "🔍 Web searches - Just ask me anything!\n"
                "⏰ Current time - Type /time\n"
                "📧 Email Management - e.g., \"Send an email to...\" or \"Check my emails\"\n"
                "📝 Todo list - Coming soon!\n\n"
                "Just type your question or command!"
            )
            return intro
        
        async def time_command(args: str, data: Dict[str, Any]) -> str:
            """Handle the /time command."""
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return f"Current time: {current_time}\nDate: {current_date}"
        
        # Register the handlers
        self.command_handlers["help"] = help_command
        self.command_handlers["start"] = start_command
        self.command_handlers["time"] = time_command
    
    def register_agent(self, intent: str, agent: Any):
        """Register an agent for a specific intent."""
        self.agents[intent] = agent
        logger.info(f"Registered agent for intent: {intent}")
    
    def register_command(self, command: str, handler: Callable):
        """Register a command handler."""
        self.command_handlers[command] = handler
        logger.info(f"Registered handler for command: {command}")