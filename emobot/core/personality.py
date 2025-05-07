"""
Personality module for the emobot assistant.
Defines emotional responses, tone, and interaction style.
"""
import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

class Emotion(Enum):
    """Basic emotions that the bot can express."""
    NEUTRAL = auto()
    HAPPY = auto()
    EXCITED = auto()
    CURIOUS = auto()
    THOUGHTFUL = auto()
    CONCERNED = auto()
    CONFUSED = auto()

@dataclass
class Response:
    """Template for a response with emotional tone."""
    text: str
    emotion: Emotion = Emotion.NEUTRAL
    emoji: Optional[str] = None

class Personality:
    """Manages the assistant's personality and response style."""
    
    def __init__(self, user_preferences: Optional[Dict[str, Any]] = None):
        """Initialize the personality with optional user preferences."""
        self.user_preferences = user_preferences or {}
        self._load_response_templates()
        
    def _load_response_templates(self):
        """Load response templates for different situations."""
        self.greetings = {
            Emotion.NEUTRAL: [
                Response("Hello! How can I assist you today?", emoji="👋"),
                Response("Hi there. What can I help you with?", emoji="👋"),
            ],
            Emotion.HAPPY: [
                Response("Hello! Great to see you! How can I help today?", Emotion.HAPPY, "😊"),
                Response("Hi there! I'm happy to assist you today!", Emotion.HAPPY, "😊"),
            ],
            Emotion.EXCITED: [
                Response("Hi! I'm super excited to help you today!", Emotion.EXCITED, "🎉"),
                Response("Hello there! Ready to tackle whatever you need!", Emotion.EXCITED, "🚀"),
            ]
        }
        
        self.acknowledgements = {
            Emotion.NEUTRAL: [
                Response("I understand.", emoji="👍"),
                Response("Got it.", emoji="👌"),
            ],
            Emotion.THOUGHTFUL: [
                Response("I see, let me think about that...", Emotion.THOUGHTFUL, "🤔"),
                Response("Interesting point. Let me consider that...", Emotion.THOUGHTFUL, "💭"),
            ],
            Emotion.CONFUSED: [
                Response("I'm not quite sure I understand. Could you clarify?", Emotion.CONFUSED, "❓"),
                Response("I'm a bit confused. Can you explain that differently?", Emotion.CONFUSED, "🤨"),
            ]
        }
        
        self.search_responses = {
            Emotion.NEUTRAL: [
                Response("Let me look that up for you.", emoji="🔍"),
                Response("Searching for information...", emoji="🔎"),
            ],
            Emotion.CURIOUS: [
                Response("That's an interesting question! Let me find out...", Emotion.CURIOUS, "🧐"),
                Response("I'm curious about that too. Let me search...", Emotion.CURIOUS, "🔍"),
            ]
        }
        
        self.error_responses = {
            Emotion.NEUTRAL: [
                Response("I encountered an error. Let's try again.", emoji="⚠️"),
                Response("Something went wrong. Please try again.", emoji="🔄"),
            ],
            Emotion.CONCERNED: [
                Response("I'm having trouble with that request. Let's try something else.", Emotion.CONCERNED, "😟"),
                Response("I apologize, but I'm unable to complete that task right now.", Emotion.CONCERNED, "😔"),
            ]
        }
    
    def get_greeting(self, emotion: Emotion = Emotion.NEUTRAL) -> Response:
        """Get a random greeting with the specified emotion."""
        if emotion not in self.greetings:
            emotion = Emotion.NEUTRAL
        return random.choice(self.greetings[emotion])
    
    def get_acknowledgement(self, emotion: Emotion = Emotion.NEUTRAL) -> Response:
        """Get a random acknowledgement with the specified emotion."""
        if emotion not in self.acknowledgements:
            emotion = Emotion.NEUTRAL
        return random.choice(self.acknowledgements[emotion])
    
    def get_search_response(self, emotion: Emotion = Emotion.NEUTRAL) -> Response:
        """Get a random search response with the specified emotion."""
        if emotion not in self.search_responses:
            emotion = Emotion.NEUTRAL
        return random.choice(self.search_responses[emotion])
    
    def get_error_response(self, emotion: Emotion = Emotion.CONCERNED) -> Response:
        """Get a random error response with the specified emotion."""
        if emotion not in self.error_responses:
            emotion = Emotion.CONCERNED
        return random.choice(self.error_responses[emotion])
    
    def format_response(self, response: Response) -> str:
        """Format a response with emoji if available."""
        if response.emoji:
            return f"{response.emoji} {response.text}"
        return response.text
    
    def determine_emotion(self, context: Dict[str, Any]) -> Emotion:
        """Determine the appropriate emotion based on context."""
        # This is a simple example - could be expanded with more sophisticated logic
        if context.get("error"):
            return Emotion.CONCERNED
            
        if context.get("search"):
            return Emotion.CURIOUS
            
        if context.get("user_mood") == "positive":
            return Emotion.HAPPY
            
        if context.get("uncertain"):
            return Emotion.THOUGHTFUL
            
        return Emotion.NEUTRAL