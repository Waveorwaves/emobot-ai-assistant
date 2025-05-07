# emobot/services/gemini_service.py
"""
Gemini service for the emobot assistant.
Handles interactions with Google's Gemini API.
"""
import google.generativeai as genai
from typing import Dict, Any, List
import asyncio
from emobot.core.config import GEMINI_API_KEY, GEMINI_MODEL, logger

class GeminiService:
    """Service for interacting with Google's Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini service."""
        self.api_key = GEMINI_API_KEY
        self.model_name = GEMINI_MODEL
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        try:
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                tools=self._get_tools()
            )
            logger.info(f"Initialized Gemini model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {e}")
            raise
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Define tools available to the model."""
        return [
            {
                "function_declarations": [
                    {
                        "name": "get_weather",
                        "description": "Get the weather for a given city",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "The city name"}
                            },
                            "required": ["city"]
                        }
                    }
                ]
            }
        ]
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a response from the Gemini model."""
        try:
            # Log the request
            logger.info(f"Sending prompt to Gemini: {prompt[:50]}...")
            
            # Start a chat session
            chat = self.model.start_chat()
            
            # Send the prompt to the model asynchronously
            logger.info("Calling Gemini API...")
            response = await genai.generative_models_async.generate_content_async(
                model=self.model_name,
                contents=prompt,
                generation_config=self.model.generation_config,
                safety_settings=self.model.safety_settings,
                tools=self._get_tools()
            )
            
            # Log success
            logger.info("Received response from Gemini API")
            
            # Return the response text
            return response.text
        except Exception as e:
            # Log the full exception details
            import traceback
            logger.error(f"Error generating response from Gemini: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def process_message(self, message: str) -> str:
        """Process a message with Gemini API."""
        try:
            response = await self.generate_response(message)
            return response
        except Exception as e:
            logger.error(f"Error processing message with Gemini: {e}")
            return f"Sorry, I encountered an error processing your message."

    def create_system_prompt(self, personality: Dict[str, Any]) -> str:
        """Create a system prompt for the model."""
        system_prompt = f"""
        You are a helpful AI assistant named {personality.get('name', 'EmoBot')}.
        Your personality:
        - Helpfulness: {personality.get('helpfulness', 'high')}
        - Creativity: {personality.get('creativity', 'medium')}
        - Friendliness: {personality.get('friendliness', 'high')}
        
        Keep responses concise and helpful. 
        If you don't know something, say so.
        
        Available commands:
        /help - Show help message
        /start - Start or restart the bot
        /time - Show the current time
        """
        return system_prompt

    async def generate_contextualized_response(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response with conversation context."""
        try:
            # Format conversation history
            formatted_history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg.get("role") == "user" else "model"
                    formatted_history.append({
                        "role": role,
                        "parts": [{"text": msg.get("content", "")}]
                    })
            
            # Add current prompt
            all_content = formatted_history + [{"role": "user", "parts": [{"text": prompt}]}]
            
            # Generate response
            chat = self.model.start_chat(history=formatted_history)
            response = await asyncio.to_thread(
                chat.send_message,
                prompt
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating contextualized response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    
    async def handle_task_request(self, user_message: str, user_id: str) -> str:
        """Handle todo list requests using MCP approach."""
        from emobot.core.task_context import TaskContext
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        # Initialize task context
        task_context = TaskContext(user_id)
        
        # Get current tasks context
        current_tasks = task_context.get_tasks_context()
        
        # Create a prompt that teaches the model how to handle tasks
        task_prompt = f"""
        You are a helpful AI assistant managing a todo list. The user will give you instructions related to their tasks.
        
        {current_tasks}
        
        The user says: "{user_message}"
        
        First, determine what the user wants to do with their tasks. Then respond with EXACTLY ONE of these action types on the first line:
        - add task: [task title] | [due date in YYYY-MM-DD format, optional]
        - complete task: [task number or title]
        - delete task: [task number or title]
        - list tasks
        
        Follow this with a helpful and friendly explanation about what you did. Be brief but polite.
        """
        
        # Get the LLM's interpretation of the task request using ThreadPoolExecutor
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            llm_response = await loop.run_in_executor(
                executor,
                lambda: self.model.generate_content(task_prompt).text
            )
        
        # Execute the interpreted action
        action_result = task_context.execute_task_action(llm_response)
        
        # If the action was to list tasks, just return the list
        if "list tasks" in llm_response.lower():
            return action_result
        
        # Get updated task list
        updated_tasks = task_context.get_tasks_context()
        
        # Generate a user-friendly response
        response_prompt = f"""
        The user asked: "{user_message}"
        
        You performed this action: {action_result}
        
        {updated_tasks}
        
        Give a friendly, concise response explaining what you did and showing the current state of their tasks.
        Only mention relevant tasks, not the entire list unless specifically requested.
        """
        
        # Get final response using ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            final_response = await loop.run_in_executor(
                executor,
                lambda: self.model.generate_content(response_prompt).text
            )
        
        return final_response