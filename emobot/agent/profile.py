import json
import os
from typing import Dict, Any, Optional

class ProfileManager:
    """
    Manages user profile information (Name, Role, Style, etc.)
    """
    def __init__(self, memory_dir: str = "agent_memory"):
        self.memory_dir = memory_dir
        self.profile_file = os.path.join(memory_dir, "user_profile.json")
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        """Load profile from file"""
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profile: {e}")
        
        # Default profile
        return {
            "name": "Yifei Wang",
            "role": "MS in Applied Data Science @ UChicago",
            "languages": ["English", "Chinese"],
            "communication_style": {
                "professors": "formal, structured, and polite",
                "family": "casual, warm, sometimes with emojis",
                "unfamiliar": "short, polite, and neutral"
            },
            "interests": ["LLMs", "ReAct agents", "Emobot project", "causal inference"],
            "description": "" # For the free-text description field in UI
        }

    def save_profile(self):
        """Save profile to file"""
        os.makedirs(self.memory_dir, exist_ok=True)
        try:
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(self.profile, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving profile: {e}")

    def get_profile(self) -> Dict[str, Any]:
        """Get current profile"""
        return self.profile

    def update_profile(self, updates: Dict[str, Any]):
        """Update profile with new values"""
        for key, value in updates.items():
            if key in self.profile:
                if isinstance(self.profile[key], dict) and isinstance(value, dict):
                    self.profile[key].update(value)
                else:
                    self.profile[key] = value
        self.save_profile()

    def get_communication_style(self, contact_type: str) -> str:
        """Get communication style for specific contact type"""
        styles = self.profile.get("communication_style", {})
        return styles.get(contact_type, styles.get("unfamiliar", "polite and professional"))
