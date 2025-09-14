from typing import List, Dict, Any, Optional
from collections import deque, defaultdict
import json
import os
from datetime import datetime
import pickle

class MemoryManager:
    """
    Memory Management Module: Manages short-term and long-term memory
    
    - Short-term memory: Current conversation context and task history
    - Long-term memory: User habits, preferences, and historical interaction patterns
    """

    def __init__(self, short_term_limit: int = 20, memory_dir: str = "agent_memory"):
        """
        Initialize memory manager

        Args:
            short_term_limit: Short-term memory capacity limit
            memory_dir: Long-term memory storage directory
        """
        # Short-term memory: Current session conversation history
        self.short_term_memory = deque(maxlen=short_term_limit)
        
        # Working memory: Current task intermediate state
        self.working_memory = {}
        
        # Long-term memory storage directory
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
        # User habit statistics
        self.user_patterns = self._load_user_patterns()
        
        # Episodic memory: Important historical interactions
        self.episodic_memory = self._load_episodic_memory()
        
        # Semantic memory: Domain knowledge and rules
        self.semantic_memory = self._load_semantic_memory()

    # ========== Short-term Memory Management ==========

    def add_to_short_term(self, entry: Dict[str, Any]):
        """Add entry to short-term memory"""
        entry["timestamp"] = datetime.now().isoformat()
        self.short_term_memory.append(entry)
        
        # Also update user patterns
        self._update_user_patterns(entry)

    def get_short_term_history(self) -> List[Dict[str, Any]]:
        """Get short-term memory history"""
        return list(self.short_term_memory)

    def get_formatted_history(self, max_entries: int = 10) -> str:
        """Format short-term memory as prompt"""
        if not self.short_term_memory:
            return "No history records."

        # Get recent records
        recent_entries = list(self.short_term_memory)[-max_entries:]
        formatted_history = []
        
        for entry in recent_entries:
            if "user_input" in entry:
                formatted_history.append(f"User: {entry['user_input']}")
            if "thought" in entry:
                formatted_history.append(f"Thought: {entry['thought']}")
            if "action" in entry:
                formatted_history.append(f"Action: {entry['action']}")
            if "observation" in entry:
                formatted_history.append(f"Observation: {entry['observation']}")
            if "response" in entry:
                formatted_history.append(f"Response: {entry['response']}")
            if "tool_call_result" in entry:
                formatted_history.append(f"Tool Call Result: {entry['tool_call_result']}")
            if "tool_call_error" in entry:
                formatted_history.append(f"Tool Call Error: {entry['tool_call_error']}")
        
        return "\n".join(formatted_history)

    def clear_short_term(self):
        """Clear short-term memory"""
        self.short_term_memory.clear()
        self.working_memory.clear()

    # ========== Working Memory Management ==========
    
    def update_working_memory(self, key: str, value: Any):
        """Update specific information in working memory"""
        self.working_memory[key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
    
    def get_from_working_memory(self, key: str) -> Optional[Any]:
        """Retrieve information from working memory"""
        if key in self.working_memory:
            return self.working_memory[key]["value"]
        return None

    # ========== Long-term Memory Management ==========
    
    def save_to_long_term(self, memory_type: str, key: str, data: Any):
        """Save to long-term memory"""
        file_path = os.path.join(self.memory_dir, f"{memory_type}_{key}.pkl")
        
        memory_entry = {
            "data": data,
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None
        }
        
        with open(file_path, 'wb') as f:
            pickle.dump(memory_entry, f)
        
        print(f"Saved to long-term memory: {memory_type}/{key}")

    def retrieve_from_long_term(self, memory_type: str, key: str) -> Optional[Any]:
        """Retrieve from long-term memory"""
        file_path = os.path.join(self.memory_dir, f"{memory_type}_{key}.pkl")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'rb') as f:
                memory_entry = pickle.load(f)
            
            # Update access information
            memory_entry["access_count"] += 1
            memory_entry["last_accessed"] = datetime.now().isoformat()
            
            with open(file_path, 'wb') as f:
                pickle.dump(memory_entry, f)
            
            return memory_entry["data"]
        except Exception as e:
            print(f"Failed to read long-term memory: {e}")
            return None

    # ========== User Pattern Learning ==========
    
    def _load_user_patterns(self) -> Dict[str, Any]:
        """Load user behavior patterns"""
        patterns_file = os.path.join(self.memory_dir, "user_patterns.json")
        
        if os.path.exists(patterns_file):
            with open(patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "intent_frequency": defaultdict(int),
            "tool_usage": defaultdict(int),
            "interaction_times": [],
            "common_entities": defaultdict(list),
            "preferences": {}
        }
    
    def _save_user_patterns(self):
        """Save user behavior patterns with safe file writing"""
        patterns_file = os.path.join(self.memory_dir, "user_patterns.json")
        temp_file = patterns_file + ".tmp"
        backup_file = patterns_file + ".backup"
        
        try:
            # Create backup
            if os.path.exists(patterns_file):
                import shutil
                shutil.copy2(patterns_file, backup_file)
            
            # Convert defaultdict to regular dict for JSON serialization
            patterns_to_save = {
                "intent_frequency": dict(self.user_patterns["intent_frequency"]),
                "tool_usage": dict(self.user_patterns["tool_usage"]),
                "interaction_times": self.user_patterns["interaction_times"][-100:],  # Keep only the last 100
                "common_entities": dict(self.user_patterns["common_entities"]),
                "preferences": self.user_patterns["preferences"]
            }
            
            # Write to temp file first
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_to_save, f, ensure_ascii=False, indent=2)
            
            # Verify temp file
            with open(temp_file, 'r', encoding='utf-8') as f:
                json.load(f)
            
            # Atomic move
            os.replace(temp_file, patterns_file)
            
            # Clean up backup
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
        except Exception as e:
            print(f"❌ Failed to save user patterns: {e}")
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Restore from backup
            if os.path.exists(backup_file):
                try:
                    os.replace(backup_file, patterns_file)
                    print("✅ Restored user patterns file from backup")
                except Exception as restore_error:
                    print(f"❌ Failed to restore user patterns backup: {restore_error}")
    
    def _update_user_patterns(self, entry: Dict[str, Any]):
        """Update user behavior patterns"""
        # Update intent frequency
        if "intent" in entry:
            self.user_patterns["intent_frequency"][entry["intent"]] += 1
        
        # Update tool usage frequency
        if "action" in entry and isinstance(entry["action"], str):
            try:
                action_data = json.loads(entry["action"])
                if "tool_name" in action_data:
                    self.user_patterns["tool_usage"][action_data["tool_name"]] += 1
            except:
                pass
        
        # Record interaction time
        self.user_patterns["interaction_times"].append(datetime.now().hour)
        
        # Periodically save
        if len(self.short_term_memory) % 5 == 0:
            self._save_user_patterns()
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preference analysis"""
        return {
            "most_used_intents": sorted(
                self.user_patterns["intent_frequency"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "most_used_tools": sorted(
                self.user_patterns["tool_usage"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "active_hours": self._analyze_active_hours(),
            "preferences": self.user_patterns["preferences"]
        }
    
    def _analyze_active_hours(self) -> List[int]:
        """Analyze user active hours"""
        if not self.user_patterns["interaction_times"]:
            return []
        
        hour_counts = defaultdict(int)
        for hour in self.user_patterns["interaction_times"]:
            hour_counts[hour] += 1
        
        # Return the 3 most active hours
        return [h for h, _ in sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    def update_preference(self, key: str, value: Any):
        """Update user preference settings"""
        self.user_patterns["preferences"][key] = value
        self._save_user_patterns()

    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            try:
                return str(obj)
            except:
                return f"Object of type {type(obj).__name__}"
        elif hasattr(obj, 'content'):
            return str(obj.content)
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            return obj

    # ========== Episodic Memory Management ==========
    
    def save_important_episode(self, episode: Dict[str, Any]):
        """Save important interaction fragments with safe file writing"""
        # Ensure all episode data is serializable
        serializable_episode = self._make_serializable(episode)
        
        self.episodic_memory.append({
            "episode": serializable_episode,
            "timestamp": datetime.now().isoformat(),
            "importance": episode.get("importance", "normal")
        })
        
        # Keep only the last 50 important fragments
        self.episodic_memory = self.episodic_memory[-50:]
        
        # Safe file writing
        self._safe_write_episodic_memory()
    
    def _safe_write_episodic_memory(self):
        """Safely write episodic memory to file using atomic operations"""
        episodic_file = os.path.join(self.memory_dir, "episodic_memory.json")
        temp_file = episodic_file + ".tmp"
        backup_file = episodic_file + ".backup"
        
        try:
            # Create backup of current file if it exists
            if os.path.exists(episodic_file):
                import shutil
                shutil.copy2(episodic_file, backup_file)
            
            # Write to temporary file first
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.episodic_memory, f, ensure_ascii=False, indent=2)
            
            # Verify the temporary file is valid JSON
            with open(temp_file, 'r', encoding='utf-8') as f:
                json.load(f)
            
            # Atomic move: rename temp file to actual file
            os.replace(temp_file, episodic_file)
            
            # Clean up backup if everything succeeded
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
        except Exception as e:
            print(f"❌ Failed to write episodic memory: {e}")
            
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Restore from backup if available
            if os.path.exists(backup_file):
                try:
                    os.replace(backup_file, episodic_file)
                    print("✅ Restored episodic memory file from backup")
                except Exception as restore_error:
                    print(f"❌ Failed to restore from backup: {restore_error}")
            
            # Revert memory to last known good state
            self._load_episodic_memory()
    
    def _load_episodic_memory(self) -> List[Dict[str, Any]]:
        """Load episodic memory with error recovery"""
        episodic_file = os.path.join(self.memory_dir, "episodic_memory.json")
        backup_file = episodic_file + ".backup"
        
        # Try to load the main file
        if os.path.exists(episodic_file):
            try:
                with open(episodic_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ Successfully loaded episodic memory: {len(data)} records")
                    return data
            except json.JSONDecodeError as e:
                print(f"❌ Main file JSON format error: {e}")
                
                # Try to load from backup
                if os.path.exists(backup_file):
                    try:
                        with open(backup_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            print(f"✅ Restored episodic memory from backup: {len(data)} records")
                            
                            # Try to repair the main file
                            try:
                                with open(episodic_file, 'w', encoding='utf-8') as f:
                                    json.dump(data, f, ensure_ascii=False, indent=2)
                                print("✅ Main file repaired successfully")
                            except Exception as repair_error:
                                print(f"❌ Failed to repair main file: {repair_error}")
                            
                            return data
                    except json.JSONDecodeError as backup_error:
                        print(f"❌ Backup file also corrupted: {backup_error}")
        
        # If all else fails, return empty list
        print("⚠️ Cannot load episodic memory, using empty list")
        return []
    
    def search_similar_episodes(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar historical interaction fragments"""
        # Simple keyword matching, future use vector similarity
        results = []
        query_lower = query.lower()
        
        for episode in self.episodic_memory:
            # Use ensure_ascii=False to keep Chinese characters
            episode_text = json.dumps(episode["episode"], ensure_ascii=False).lower()
            if any(word in episode_text for word in query_lower.split()):
                results.append(episode)
        
        return results[:limit]

    # ========== Semantic Memory Management ==========
    
    def _load_semantic_memory(self) -> Dict[str, Any]:
        """Load semantic memory (domain knowledge)"""
        semantic_file = os.path.join(self.memory_dir, "semantic_memory.json")
        
        if os.path.exists(semantic_file):
            with open(semantic_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Initialize some basic domain knowledge
        return {
            "rules": {
                "email_etiquette": "When sending emails, use polite salutations and endings",
                "search_tips": "When searching, using specific keywords will yield better results",
                "todo_management": "Tasks should be specific, executable, and have deadlines"
            },
            "facts": {},
            "concepts": {}
        }
    
    def add_semantic_knowledge(self, category: str, key: str, value: str):
        """Add semantic knowledge with safe file writing"""
        if category not in self.semantic_memory:
            self.semantic_memory[category] = {}
        
        self.semantic_memory[category][key] = value
        
        # Safe file writing
        self._safe_write_semantic_memory()
    
    def _safe_write_semantic_memory(self):
        """Safely write semantic memory to file"""
        semantic_file = os.path.join(self.memory_dir, "semantic_memory.json")
        temp_file = semantic_file + ".tmp"
        backup_file = semantic_file + ".backup"
        
        try:
            # Create backup
            if os.path.exists(semantic_file):
                import shutil
                shutil.copy2(semantic_file, backup_file)
            
            # Write to temp file first
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.semantic_memory, f, ensure_ascii=False, indent=2)
            
            # Verify temp file
            with open(temp_file, 'r', encoding='utf-8') as f:
                json.load(f)
            
            # Atomic move
            os.replace(temp_file, semantic_file)
            
            # Clean up backup
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
        except Exception as e:
            print(f"❌ Failed to save semantic memory: {e}")
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Restore from backup
            if os.path.exists(backup_file):
                try:
                    os.replace(backup_file, semantic_file)
                    print("✅ Restored semantic memory file from backup")
                except Exception as restore_error:
                    print(f"❌ Failed to restore semantic memory backup: {restore_error}")
    
    def get_relevant_knowledge(self, context: str) -> List[str]:
        """Get relevant domain knowledge"""
        relevant = []
        context_lower = context.lower()
        
        # Search all semantic memory
        for category, items in self.semantic_memory.items():
            for key, value in items.items():
                if key.lower() in context_lower or any(word in context_lower for word in key.lower().split("_")):
                    relevant.append(f"[{category}] {value}")
        
        return relevant

    # ========== Memory Statistics and Maintenance ==========
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            "short_term_size": len(self.short_term_memory),
            "working_memory_keys": list(self.working_memory.keys()),
            "episodic_count": len(self.episodic_memory),
            "user_patterns": {
                "total_interactions": sum(self.user_patterns["intent_frequency"].values()),
                "unique_intents": len(self.user_patterns["intent_frequency"]),
                "unique_tools": len(self.user_patterns["tool_usage"])
            },
            "semantic_categories": list(self.semantic_memory.keys())
        }
    
    def cleanup_old_memories(self, days: int = 30):
        """Clean up old memory files"""
        # Implement memory cleanup logic
        pass