"""
Memory management for the emobot assistant.
Handles conversation history and user preferences.
"""
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from emobot.core.config import MEMORY_DIR, USER_DATA_DIR, logger

class MemoryManager:
    """Manages conversation history and user preferences."""
    
    def __init__(self, user_id: str):
        """Initialize the memory manager for a specific user."""
        self.user_id = user_id
        self.user_data_path = USER_DATA_DIR / f"{user_id}.json"
        self.memory_path = MEMORY_DIR / f"{user_id}.json"
        self.conversation_history: List[Dict[str, Any]] = []
        self.user_preferences: Dict[str, Any] = {}
        self.load_data()
    
    def load_data(self):
        """Load user data and conversation history from storage."""
        # Load user preferences
        if self.user_data_path.exists():
            try:
                with open(self.user_data_path, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
                logger.info(f"Loaded preferences for user {self.user_id}")
            except Exception as e:
                logger.error(f"Error loading preferences for user {self.user_id}: {e}")
                self.user_preferences = {}
        
        # Load conversation history
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                logger.info(f"Loaded conversation history for user {self.user_id}")
            except Exception as e:
                logger.error(f"Error loading conversation history for user {self.user_id}: {e}")
                self.conversation_history = []
    
    def save_data(self):
        """Save user data and conversation history to storage."""
        # Save user preferences
        try:
            with open(self.user_data_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved preferences for user {self.user_id}")
        except Exception as e:
            logger.error(f"Error saving preferences for user {self.user_id}: {e}")
        
        # Save conversation history
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved conversation history for user {self.user_id}")
        except Exception as e:
            logger.error(f"Error saving conversation history for user {self.user_id}: {e}")
    
    def add_message(self, role: str, text: str, timestamp: Optional[float] = None):
        """Add a message to the conversation history."""
        if timestamp is None:
            timestamp = time.time()
        
        message = {
            "role": role,  # 'user' or 'assistant'
            "text": text,
            "timestamp": timestamp
        }
        
        self.conversation_history.append(message)
        
        # Limit conversation history to last 50 messages
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
        # Save after each message
        self.save_data()
    
    def get_conversation_context(self, n_messages: int = 10) -> List[Dict[str, Any]]:
        """Get the last n messages of conversation history."""
        return self.conversation_history[-n_messages:] if n_messages > 0 else []
    
    def update_preference(self, key: str, value: Any):
        """Update a user preference."""
        self.user_preferences[key] = value
        self.save_data()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        return self.user_preferences.get(key, default)
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.save_data()
    
    def get_topic_history(self, topic: str) -> List[Dict[str, Any]]:
        """Get conversation history related to a specific topic.
        
        This is a simple implementation that just checks if the topic
        word appears in the message text.
        """
        return [
            message for message in self.conversation_history
            if topic.lower() in message.get("text", "").lower()
        ]

    def get_conversation_history(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history formatted for Gemini API."""
        history = []
        
        # Get most recent messages
        recent_messages = self.get_conversation_context(max_messages)
        
        # Format for Gemini API
        for message in recent_messages:
            role = "user" if message["role"] == "user" else "model"
            history.append({
                "role": role,
                "parts": [{"text": message["text"]}]
            })
        
        return history