import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from smolagents import ToolCallingAgent

from .model_manager import ModelManager
from .perception import PerceptionModule
from .memory import MemoryManager
from .actions import ActionExecutor
from .tool_wrapper import MCPToolWrapper

class ReasoningModule:
    """
    Reasoning Module: Implements ReAct (Reasoning + Acting) loop
    
    Uses smolagents framework to interact with language models through think-act-observe cycles.
    Integrates perception, memory, and action modules to form a complete cognitive process.
    """

    def __init__(self, 
                 model_id: str = "gpt-4", 
                 server_url: str = "http://127.0.0.1:8080",
                 system_prompt_path: str = "configs/system_prompt.md",
                 use_local_model: bool = False):
        """
        Initialize reasoning module

        Args:
            model_id: Model identifier
            server_url: MCP tool server URL
            system_prompt_path: System prompt path
            use_local_model: Whether to use local model
        """
        # Initialize sub-modules
        self.perception = PerceptionModule()
        self.memory = MemoryManager()
        self.action_executor = ActionExecutor(server_url)
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt(system_prompt_path)
        
        # Get available tools and create smolagents Tool objects
        self.tools = self._initialize_tools()
        
        # Initialize model manager
        self.model_manager = ModelManager()
        
        # Create model and agent
        model = self.model_manager.create_model(model_id)
        if not model:
            raise Exception("Unable to create any available model")
        
        self.agent: Union[ToolCallingAgent, Any] = self.model_manager.create_agent(
            model=model,
            tools=list(self.tools.values()),
            system_prompt=self.system_prompt
        )
        
        if not self.agent:
            raise Exception("Unable to create agent")
        
        # ReAct loop configuration
        self.max_steps = 10
        self.thinking_patterns = {
            "analyze": "Let me analyze this problem...",
            "plan": "I need to create a plan to solve this problem...",
            "tool_needed": "I need to use tools to get information...",
            "synthesize": "Based on the information obtained, I can conclude...",
            "clarify": "I need to clarify some details..."
        }
        
        # Confirmation system
        self.pending_confirmation = None  # Stores pending action that needs confirmation
        self.confirmation_callback = None  # Callback function for user confirmation
        
        # Define sensitive operations that require confirmation
        self.sensitive_operations = {
            "email": ["send_email"],
            "calendar": ["create_event", "delete_event", "send_invitation"],
            "todo_list": ["delete_task", "clear_completed"]
        }

    def _load_system_prompt(self, prompt_path: str) -> str:
        """Load system prompt from file"""
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Failed to load system prompt: {e}")
            return "You are a helpful AI assistant."

    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize available tools"""
        try:
            # Get available tools from MCP server
            available_tools = self.action_executor.get_available_tools()
            
            # Create smolagents Tool objects
            tools = {}
            for tool_info in available_tools:
                tool_name = tool_info['name']
                tools[tool_name] = MCPToolWrapper(self.action_executor, tool_name)
            
            return tools
        except Exception as e:
            logging.error(f"Failed to initialize tools: {e}")
            return {}

    def process_query(self, query: str) -> str:
        """
        Process user query using ReAct loop with conversation context and episodic memory

        Args:
            query: User's query

        Returns:
            Final response to user
        """
        logging.debug(f"Processing query: {query}")
        
        # Get conversation history for context (short-term memory)
        conversation_history = self.memory.get_formatted_history(max_entries=5)
        logging.debug(f"Conversation history available: {bool(conversation_history and conversation_history != 'No history records.')}")
        
        # 🔥 NEW: Retrieve relevant episodic memories
        relevant_episodes = self.memory.search_similar_episodes(query, limit=3)
        episodic_context = ""
        if relevant_episodes:
            episodic_context = self._format_episodic_context(relevant_episodes)
            logging.debug(f"Found {len(relevant_episodes)} relevant past experiences")
        else:
            logging.debug("No relevant past experiences found")
        
        # Combine all context information
        full_context = self._combine_context(conversation_history, episodic_context)
        
        # Update memory with new query
        self.memory.add_to_short_term({"user_input": query})
        
        # Create execution plan with enhanced context
        plan = self._create_execution_plan(query, full_context)
        logging.debug(f"Plan created with context: {plan.get('context_used', False)}")
        
        # Execute ReAct loop with enhanced context
        result = self._run_tool_calling_loop(query, plan, full_context)
        
        # Update memory with result
        self.memory.save_important_episode({
            "query": query,
            "result": result,
            "plan": plan
        })
        
        return result

    def _format_episodic_context(self, episodes: List[Dict[str, Any]]) -> str:
        """Format episodic memories into context string"""
        if not episodes:
            return ""
        
        context = "\n\nRelevant Past Experiences:\n"
        for i, episode in enumerate(episodes, 1):
            episode_data = episode.get("episode", {})
            query_text = episode_data.get("query", "Unknown query")
            result_text = episode_data.get("result", "No result")
            timestamp = episode.get("timestamp", "Unknown time")
            
            # Truncate long results for context
            if len(result_text) > 150:
                result_text = result_text[:150] + "..."
            
            context += f"{i}. [{timestamp[:10]}] Query: {query_text}\n"
            context += f"   Result: {result_text}\n\n"
        
        return context

    def _combine_context(self, conversation_history: str, episodic_context: str) -> str:
        """Combine conversation history and episodic context"""
        combined = ""
        
        # Add conversation history
        if conversation_history and conversation_history != "No history records.":
            combined += conversation_history
        
        # Add episodic context
        if episodic_context:
            combined += episodic_context
        
        return combined if combined else "No history records."

    def _create_execution_plan(self, query: str, conversation_history: str = "") -> dict:
        """
        Create execution plan for the query with conversation context

        Args:
            query: User's query
            conversation_history: Previous conversation context

        Returns:
            Execution plan dictionary
        """
        context_info = ""
        if conversation_history and conversation_history != "No history records.":
            context_info = f"""
        
        Conversation History:
        {conversation_history}
        
        Please consider the conversation history when creating your plan. If the user is continuing a previous task or providing additional information, incorporate that context into your plan.
        """
        
        plan_prompt = f"""
        Create a detailed execution plan for the following query: "{query}"
        {context_info}

        The plan should include:
        1. Task Analysis: What needs to be done
        2. Tool Selection: Which tools might be needed
        3. Execution Steps: Step-by-step approach
        4. Expected Results: What we expect to achieve

        Available tools: {list(self.tools.keys())}

        Please provide a structured plan.
        """
        
        try:
            # Use a simple model call to create plan (suppress output)
            import sys
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            captured_stdout = io.StringIO()
            captured_stderr = io.StringIO()
            
            with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
                response = self.agent.run(plan_prompt)
            
            return {
                "query": query,
                "plan": response,
                "created_at": datetime.now().isoformat(),
                "context_used": bool(conversation_history)
            }
        except Exception as e:
            # Fallback to basic plan
            return {
                "query": query,
                "plan": f"Basic plan for: {query}",
                "created_at": datetime.now().isoformat(),
                "error": str(e),
                "context_used": bool(conversation_history)
            }

    def _run_tool_calling_loop(self, query: str, plan: dict, conversation_history: str = "") -> str:
        """
        Run the ReAct tool calling loop with conversation context

        Args:
            query: User's query
            plan: Execution plan
            conversation_history: Previous conversation context

        Returns:
            Final response
        """
        tool_results = []
        current_thought = ""
        step = 1
        executed_tools = []  # Track executed tool calls to prevent duplicates
        
        while step <= self.max_steps:
            logging.debug(f"ReAct Step {step}/{self.max_steps}")
            
            # Build thought prompt with context
            thought_prompt = self._build_thought_prompt(query, step, current_thought, tool_results, plan, conversation_history)
            
            # Get model's thought (suppress any intermediate output from smolagents)
            try:
                import sys
                import io
                from contextlib import redirect_stdout, redirect_stderr
                
                # Capture any output from smolagents
                captured_stdout = io.StringIO()
                captured_stderr = io.StringIO()
                
                with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
                    thought_response = self.agent.run(thought_prompt)
                
                current_thought = str(thought_response)
                logging.debug(f"Thought: {current_thought[:200]}...")
                
                # Log any captured output for debugging
                stdout_content = captured_stdout.getvalue()
                stderr_content = captured_stderr.getvalue()
                if stdout_content:
                    logging.debug(f"Agent stdout: {stdout_content}")
                if stderr_content:
                    logging.debug(f"Agent stderr: {stderr_content}")
                    
            except Exception as e:
                logging.error(f"Thought generation failed: {e}")
                break
            
            # Extract tool call or final answer
            tool_call = self._extract_tool_call(query, current_thought)
            final_answer = self._extract_final_answer(current_thought)
            
            # Check if this is an action request that requires tool execution
            requires_tool = self._check_requires_tool_execution(query, current_thought)
            
            if requires_tool and not tool_call:
                logging.debug("WARNING: Action requested but no tool call extracted!")
                logging.debug("Attempting to generate tool call from context...")
                tool_call = self._generate_tool_call_from_context(query, current_thought)
            
            # Check for duplicate tool calls
            if tool_call:
                tool_signature = f"{tool_call['tool_name']}:{tool_call['parameters'].get('operation', '')}:{tool_call['parameters'].get('recipient', '')}"
                if tool_signature in executed_tools:
                    logging.debug(f"Duplicate tool call detected: {tool_signature}")
                    logging.debug("Skipping duplicate execution")
                    # If we have results and a duplicate is attempted, provide final answer
                    if tool_results:
                        return self._generate_final_answer_from_results(query, tool_results)
                    tool_call = None
            
            if final_answer and not tool_results:
                if requires_tool:
                    logging.debug("WARNING: Final answer provided without tool execution!")
                    logging.debug("Blocking premature final answer")
                    final_answer = ""  # Clear the final answer to force tool execution
                else:
                    logging.debug("Final Answer found!")
                    return final_answer
            elif final_answer:
                logging.debug(f"Final Answer found after {len(tool_results)} tool executions!")
                return final_answer
            
            if tool_call:
                logging.debug(f"Executing tool: {tool_call['tool_name']}")
                logging.debug(f"With parameters: {tool_call['parameters']}")
                
                # Check if this operation needs confirmation
                if self.needs_confirmation(tool_call['tool_name'], tool_call['parameters']):
                    logging.debug("This operation requires user confirmation")
                    
                    # Store pending action
                    self.pending_confirmation = {
                        'tool_name': tool_call['tool_name'],
                        'parameters': tool_call['parameters'],
                        'query': query,
                        'step': step
                    }
                    
                    # Generate confirmation request
                    confirmation_msg = self.request_confirmation(
                        tool_call['tool_name'], 
                        tool_call['parameters']
                    )
                    
                    return confirmation_msg
                
                # Execute tool (non-sensitive operations)
                result = self.action_executor.execute_action(
                    tool_call['tool_name'], 
                    tool_call['parameters']
                )
                
                # Track this execution
                tool_signature = f"{tool_call['tool_name']}:{tool_call['parameters'].get('operation', '')}:{tool_call['parameters'].get('recipient', '')}"
                executed_tools.append(tool_signature)
                
                # Record tool result
                tool_results.append({
                    'step': step,
                    'tool': tool_call['tool_name'],
                    'parameters': tool_call['parameters'],
                    'result': result
                })
                
                # Display tool result
                if result.get('status') == 'success':
                    result_str = str(result.get('result', result))
                    logging.debug(f"Tool result: {result_str[:200]}...")
                else:
                    error_msg = result.get('error_message', 'Unknown error')
                    logging.error(f"Tool failed: {error_msg}")
            else:
                logging.debug("No tool call or final answer detected")
                break
            
            step += 1
        
        # If we reach here, generate fallback answer
        return self._generate_fallback_answer(query, tool_results, current_thought)

    def _build_thought_prompt(self, query: str, step: int, current_thought: str, 
                            tool_results: list, plan: dict, conversation_history: str = "") -> str:
        """Build thought prompt for current step with conversation context"""
        
        # Add enhanced context if available (includes both conversation history and episodic memory)
        context_section = ""
        if conversation_history and conversation_history != "No history records.":
            context_section = f"""
        
        Context Information:
        {conversation_history}
        
        IMPORTANT: Consider both the recent conversation history and any relevant past experiences when making decisions. If the user is continuing a previous task or providing additional information (like an email address after asking to send an email), use that context to understand what they want. Past experiences can help you understand user preferences and patterns.
        """
        
        prompt = f"""
        You are in step {step} of the ReAct loop.

        User Query: {query}
        {context_section}

        Context Information:
        Plan: {plan.get('plan', 'No plan available')}

        Current Thought State:
        {current_thought if current_thought else "Initial State"}

        History of Tool Calls:
        """
        
        if tool_results:
            for i, result in enumerate(tool_results, 1):
                prompt += f"""
        Step {result['step']}: Tool Call {result['tool']}
        Parameters: {result['parameters']}
        """
                # For email tools, provide more detailed result information
                if result['tool'] == 'email' and 'emails' in result['result']:
                    emails = result['result']['emails']
                    prompt += f"Result: Successfully read {len(emails)} emails from a real Gmail account\n"
                    for j, email in enumerate(emails, 1):
                        subject = email.get('subject', 'No Subject')
                        sender = email.get('from', 'Unknown Sender')
                        date = email.get('date', 'Unknown Date')
                        body_preview = email.get('body', '')[:100] + '...' if len(email.get('body', '')) > 100 else email.get('body', '')
                        prompt += f"   Real Email {j}: Subject={subject}, Sender={sender}, Date={date}\n   Content Preview: {body_preview}\n"
                else:
                    prompt += f"Result: {str(result['result'])[:300]}...\n"
        else:
            prompt += "No tool call results yet.\n"
        
        prompt += f"""

        Please think according to the following format:

        **Thought**: Analyze the current situation and decide the next action
        - If more information is needed, specify the tool to be called and its parameters
        - If enough information is available, provide the final answer

        **Action**: 
        - If a tool is needed, use JSON format:
        ```json
        {{
          "tool_name": "Tool Name",
          "parameters": {{
            "ParameterName": "ParameterValue"
          }}
        }}
        ```
        - If a final answer is available, use:
        ```
        Final Answer: Your final answer
        ```

        Please start your thinking:
        """
        return prompt

    def _extract_tool_call(self, query: str, thought: str) -> Optional[dict]:
        """Extract tool call from thought result with enhanced context awareness"""
        try:
            import re
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            matches = re.findall(json_pattern, thought, re.DOTALL)
            
            logging.debug(f"Searching for tool calls in thought...")
            logging.debug(f"Thought preview: {thought[:200]}...")
            
            if matches:
                logging.debug(f"Found {len(matches)} JSON matches")
                for i, match in enumerate(matches):
                    try:
                        tool_call = json.loads(match)
                        if "tool_name" in tool_call and "parameters" in tool_call:
                            # Validate tool name exists
                            if tool_call["tool_name"] in self.tools:
                                logging.debug(f"Valid tool call extracted: {tool_call['tool_name']}")
                                logging.debug(f"Parameters: {tool_call['parameters']}")
                                return tool_call
                            else:
                                logging.debug(f"Invalid tool name: {tool_call['tool_name']}")
                                logging.debug(f"Available tools: {list(self.tools.keys())}")
                    except json.JSONDecodeError as e:
                        logging.debug(f"JSON decode error in match {i}: {e}")
                        continue
            else:
                logging.debug("No JSON matches found, attempting intent detection...")
            
            # Enhanced intent detection based on context
            thought_lower = thought.lower()
            
            # Check if we have an email address in the thought
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', thought)
            
            # Get recent conversation history to understand context
            recent_history = self.memory.get_formatted_history(max_entries=5)
            history_lower = recent_history.lower() if recent_history else ""
            
            logging.debug(f"Email address found: {email_match.group(1) if email_match else 'None'}")
            
            # Strong email sending intent detection
            send_keywords = ['send', 'email', 'mail', 'ask', 'tell', 'notify', 'message']
            has_send_intent = any(keyword in thought_lower for keyword in send_keywords)
            has_email_in_history = any(keyword in history_lower for keyword in ['send', 'email', 'mail'])
            
            logging.debug(f"Send intent detected: {has_send_intent}")
            logging.debug(f"Email context in history: {has_email_in_history}")
            
            # If we have an email address and any indication of sending
            if email_match and (has_send_intent or has_email_in_history):
                email_address = email_match.group(1)
                logging.debug(f"Auto-generating email send command for: {email_address}")
                
                # Extract meaningful content from the query
                subject, body = self._extract_email_content(query)
                
                return {
                    "tool_name": "email",
                    "parameters": {
                        "operation": "send_email",
                        "recipient": email_address,
                        "subject": subject,
                        "body": body
                    }
                }
            
            # Fallback: if user explicitly asks to send email
            if any(phrase in thought_lower for phrase in ['send an email', 'send email', 'email to']):
                logging.debug("Email sending request detected without specific address")
                return {
                    "tool_name": "email",
                    "parameters": {
                        "operation": "send_email"
                    }
                }
            
            logging.debug("No tool call could be extracted or inferred")
            return None
            
        except Exception as e:
            logging.error(f"Tool call extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _check_requires_tool_execution(self, query: str, thought: str) -> bool:
        """Check if the query requires tool execution"""
        query_lower = query.lower()
        thought_lower = thought.lower()
        
        # Keywords that indicate action is required
        action_keywords = [
            'send', 'email', 'mail', 'create', 'add', 'delete', 'update',
            'search', 'find', 'look up', 'check', 'get', 'fetch',
            'write', 'read', 'mark', 'notify', 'ask', 'tell'
        ]
        
        # Check if query contains action keywords
        has_action = any(keyword in query_lower for keyword in action_keywords)
        
        # Check if an email address is present (strong indicator of email action)
        import re
        has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', query + thought))
        
        return has_action or has_email
    
    def _generate_tool_call_from_context(self, query: str, thought: str) -> Optional[dict]:
        """Generate tool call from context when extraction fails"""
        import re
        combined_text = query + " " + thought
        combined_lower = combined_text.lower()
        
        # Check for email address
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', combined_text)
        
        # Email sending detection
        if email_match and any(keyword in combined_lower for keyword in ['send', 'email', 'mail', 'ask', 'tell', 'notify', 'inform']):
            email_address = email_match.group(1)
            logging.debug(f"Auto-generating email tool call for: {email_address}")
            
            # Extract meaningful content from the query for subject and body
            subject, body = self._extract_email_content(query)
            
            return {
                "tool_name": "email",
                "parameters": {
                    "operation": "send_email",
                    "recipient": email_address,
                    "subject": subject,
                    "body": body
                }
            }
        
        # Calendar detection
        if any(keyword in combined_lower for keyword in ['calendar', 'schedule', 'appointment', 'meeting', 'event']):
            logging.debug("Auto-generating calendar tool call")
            
            # Check what calendar operation is needed
            if any(keyword in combined_lower for keyword in ['check', 'see', 'view', 'show', 'list', 'what']):
                return {
                    "tool_name": "calendar",
                    "parameters": {
                        "operation": "list_events"
                    }
                }
            elif any(keyword in combined_lower for keyword in ['create', 'add', 'schedule', 'book']):
                # Extract event details from context if possible
                title = self._extract_event_title(query)
                return {
                    "tool_name": "calendar",
                    "parameters": {
                        "operation": "create_event",
                        "title": title
                    }
                }
            elif any(keyword in combined_lower for keyword in ['delete', 'remove', 'cancel']):
                # For delete operations, first list events to find the right one
                return {
                    "tool_name": "calendar",
                    "parameters": {
                        "operation": "list_events"
                    }
                }
        
        # Todo list detection
        if any(keyword in combined_lower for keyword in ['todo', 'task', 'to-do', 'to do']):
            logging.debug("Auto-generating todo tool call")
            
            if any(keyword in combined_lower for keyword in ['add', 'create', 'new']):
                task_description = self._extract_task_description(query)
                return {
                    "tool_name": "todo_list",
                    "parameters": {
                        "operation": "add_task",
                        "task": task_description
                    }
                }
            else:
                return {
                    "tool_name": "todo_list",
                    "parameters": {
                        "operation": "view_list"
                    }
                }
        
        return None
    
    def _extract_email_content(self, query: str) -> tuple:
        """Extract subject and body from query using model generation for natural content"""
        try:
            # Use the model to generate natural email content
            email_generation_prompt = f"""
You need to help generate a professional email based on this request: "{query}"

Please analyze the request and create:
1. A clear, professional subject line
2. A natural, well-written email body

IMPORTANT: You must respond in exactly this format:
SUBJECT: [your subject line here]
BODY: [your email body here]

Example:
SUBJECT: Meeting Reschedule Request  
BODY: Hi,

I hope this email finds you well. I wanted to reach out regarding our meeting scheduled for tomorrow. Due to a scheduling conflict, I need to reschedule our meeting.

Would you be available to meet at a different time? Please let me know what works best for your schedule.

Best regards,
[Your name]

Now generate the email for: {query}
"""
            
            # Get model response
            response = self.agent.run(email_generation_prompt)
            response_str = str(response)
            
            logging.debug(f"Model response: {response_str[:300]}...")
            
            # Try multiple parsing patterns
            parsing_patterns = [
                # Pattern 1: SUBJECT: ... BODY: ...
                (r'SUBJECT:\s*(.+?)(?=BODY:)', r'BODY:\s*(.+)', re.IGNORECASE | re.DOTALL),
                # Pattern 2: Subject: ... Body: ...
                (r'Subject:\s*(.+?)(?=Body:)', r'Body:\s*(.+)', re.IGNORECASE | re.DOTALL),
                # Pattern 3: **Subject:** ... **Body:** ...
                (r'\*\*Subject:\*\*\s*(.+?)(?=\*\*Body:\*\*)', r'\*\*Body:\*\*\s*(.+)', re.IGNORECASE | re.DOTALL),
            ]
            
            for subject_pattern, body_pattern, flags in parsing_patterns:
                subject_match = re.search(subject_pattern, response_str, flags)
                body_match = re.search(body_pattern, response_str, flags)
                
                if subject_match and body_match:
                    subject = subject_match.group(1).strip()
                    body = body_match.group(1).strip()
                    
                    # Clean up the content
                    subject = re.sub(r'["\'\[\]]+', '', subject).strip()
                    body = re.sub(r'\s*```\s*$', '', body).strip()
                    body = re.sub(r'^\s*```\s*', '', body).strip()
                    
                    logging.debug(f"Successfully parsed model response:")
                    logging.debug(f"   Subject: {subject}")
                    logging.debug(f"   Body preview: {body[:100]}...")
                    
                    return subject, body
            
            logging.debug("Could not parse model response, using intelligent fallback")
            return self._extract_email_content_intelligent_fallback(query)
                
        except Exception as e:
            logging.error(f"Model generation failed: {e}")
            return self._extract_email_content_intelligent_fallback(query)
    
    def _extract_email_content_intelligent_fallback(self, query: str) -> tuple:
        """Intelligent fallback method for email content extraction"""
        import re
        query_lower = query.lower()
        
        # Extract email address first
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', query)
        recipient_name = "there"
        if email_match:
            email_parts = email_match.group(1).split('@')[0]
            # Try to extract name from email
            if '_' in email_parts:
                name_parts = email_parts.split('_')
                recipient_name = ' '.join(part.capitalize() for part in name_parts if part.isalpha())
            elif '.' in email_parts:
                name_parts = email_parts.split('.')
                recipient_name = ' '.join(part.capitalize() for part in name_parts if part.isalpha())
            else:
                recipient_name = email_parts.capitalize()
        
        # Analyze the intent and generate appropriate content
        if 'test' in query_lower:
            subject = "Test Email"
            body = f"Hi {recipient_name},\n\nThis is a test email to verify our email system is working properly.\n\nBest regards,\nEmobot"
            
        elif any(word in query_lower for word in ['ask', 'question', 'inquire']):
            # Extract what we're asking about
            ask_about = query
            for prefix in ['send', 'email', 'mail', 'to', 'ask', 'him', 'her', 'them', 'if', 'whether']:
                ask_about = re.sub(f'\\b{prefix}\\b', '', ask_about, flags=re.IGNORECASE)
            ask_about = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', ask_about).strip()
            
            if 'finish' in ask_about.lower() or 'complet' in ask_about.lower():
                subject = "Task Status Inquiry"
                body = f"Hi {recipient_name},\n\nI hope this email finds you well. I wanted to check in on the status of the task we discussed.\n\nHave you had a chance to complete it? Please let me know when you have a moment.\n\nBest regards,\nEmobot"
            elif 'reschedule' in ask_about.lower() or 'meeting' in ask_about.lower():
                subject = "Meeting Reschedule Request"
                body = f"Hi {recipient_name},\n\nI hope you're doing well. I need to discuss rescheduling our upcoming meeting.\n\nWould you be available to meet at a different time? Please let me know what works best for your schedule.\n\nLooking forward to hearing from you.\n\nBest regards,\nEmobot"
            else:
                subject = "Question"
                body = f"Hi {recipient_name},\n\nI hope this email finds you well. I wanted to ask you about {ask_about.strip()}.\n\nI'd appreciate your thoughts when you have a moment.\n\nBest regards,\nEmobot"
                
        elif any(word in query_lower for word in ['inform', 'tell', 'notify']):
            subject = "Information"
            body = f"Hi {recipient_name},\n\nI hope you're doing well. I wanted to share some information with you.\n\nPlease let me know if you have any questions.\n\nBest regards,\nEmobot"
            
        else:
            # Generic but personalized fallback
            subject = "Message from Emobot"
            body = f"Hi {recipient_name},\n\nI hope this email finds you well. I'm reaching out regarding your recent request.\n\nPlease let me know if you need any additional information.\n\nBest regards,\nEmobot"
        
        return subject, body
    
    def _extract_event_title(self, query: str) -> str:
        """Extract event title from query"""
        # Remove common prefixes
        title = query
        for prefix in ['create', 'add', 'schedule', 'book', 'an', 'a', 'event', 'meeting', 'appointment']:
            title = re.sub(f'^{prefix}\\s+', '', title, flags=re.IGNORECASE)
        
        # If we have something meaningful left, use it
        if title and title != query:
            return title.strip().capitalize()
        else:
            return "New Event"
    
    def _extract_task_description(self, query: str) -> str:
        """Extract task description from query"""
        # Remove common prefixes
        task = query
        for prefix in ['add', 'create', 'new', 'a', 'task', 'todo', 'to-do', 'to do']:
            task = re.sub(f'^{prefix}\\s+', '', task, flags=re.IGNORECASE)
        
        # If we have something meaningful left, use it
        if task and task != query:
            return task.strip()
        else:
            return "New Task"

    def _extract_final_answer(self, thought: str) -> str:
        """Extract final answer from thought result"""
        try:
            import re
            patterns = [
                r'Final Answer:\s*(.*?)(?=\n\n|\n$|$)',
                r'最终答案:\s*(.*?)(?=\n\n|\n$|$)',
                r'最终答案：\s*(.*?)(?=\n\n|\n$|$)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, thought, re.DOTALL)
                if match:
                    return match.group(1).strip()
            
            return ""
            
        except Exception as e:
            logging.error(f"Final answer extraction failed: {e}")
            return ""

    def _generate_final_answer_from_results(self, query: str, tool_results: list) -> str:
        """Generate final answer based on tool execution results"""
        if not tool_results:
            return "I couldn't complete the requested action."
        
        last_result = tool_results[-1]
        tool_name = last_result['tool']
        parameters = last_result['parameters']
        result = last_result['result']
        
        if result.get('status') == 'success':
            if tool_name == 'email' and parameters.get('operation') == 'send_email':
                recipient = parameters.get('recipient', 'the recipient')
                return f"I have successfully sent the email to {recipient}. {result.get('result', '')}"
            elif tool_name == 'calendar' and parameters.get('operation') == 'list_events':
                events = result.get('events', [])
                if events:
                    return f"Here are your calendar events: {result.get('result', '')}"
                else:
                    return "You have no events scheduled."
            elif tool_name == 'todo_list':
                return f"Todo list operation completed: {result.get('result', '')}"
            else:
                return f"The operation was completed successfully: {result.get('result', '')}"
        else:
            error_msg = result.get('error_message', 'Unknown error')
            return f"I encountered an error: {error_msg}"
    
    def _generate_fallback_answer(self, query: str, tool_results: list, last_thought: str) -> str:
        """Generate fallback answer"""
        try:
            # If we have tool results, format them directly
            if tool_results:
                # Check if we have calendar events to display
                for result in tool_results:
                    if result['tool'] == 'calendar' and result['parameters'].get('operation') == 'list_events':
                        calendar_result = result['result']
                        if isinstance(calendar_result, dict) and calendar_result.get('status') == 'success':
                            events = calendar_result.get('events', [])
                            if events:
                                event_list = "Here are your calendar events:\n\n"
                                for i, event in enumerate(events, 1):
                                    title = event.get('title', 'Untitled Event')
                                    start_time = event.get('start_time', 'No time specified')
                                    event_id = event.get('id', 'unknown')
                                    event_list += f"{i}. **{title}**\n   Time: {start_time}\n   ID: {event_id}\n\n"
                                return event_list
                            else:
                                return "You don't have any calendar events at the moment."
                        else:
                            return "I couldn't retrieve your calendar events. Please try again."
                
                # For other tool results, provide a generic response
                return f"I've executed the requested action. The operation completed with the following result: {str(tool_results[-1]['result'])}"
            
            # If no tool results, provide a generic response
            return "I'm ready to help you. Please let me know what you'd like me to do."
            
        except Exception as e:
            return f"I apologize, I cannot fulfill this request. Error message: {e}"

    def explain_reasoning(self, query: str) -> str:
        """Explain reasoning process"""
        explanation = f"For query '{query}', my reasoning process is as follows:\n"
        
        # Analyze query
        perceived = self.perception.process_input(query)
        explanation += f"1. Intent Recognition: {perceived.get('intent', 'general')}\n"
        explanation += f"2. Entity Recognition: {perceived.get('entities', {})}\n"
        
        # Tool selection
        if perceived.get("requires_tools"):
            explanation += f"3. Tools are needed to obtain information\n"
        else:
            explanation += f"3. Can directly answer based on knowledge\n"
        
        return explanation

    def reflect_on_performance(self) -> Dict[str, Any]:
        """Reflect on performance"""
        stats = self.memory.get_memory_stats()
        preferences = self.memory.get_user_preferences()
        
        reflection = {
            "interaction_count": stats["user_patterns"]["total_interactions"],
            "tool_effectiveness": {tool: 0.8 for tool in self.tools.keys()},
            "user_satisfaction_indicators": {
                "response_completeness": 0.85,
                "task_completion_rate": 0.9,
                "error_rate": 0.05
            },
            "improvement_suggestions": [
                "Continue optimizing tool response times",
                "Improve error handling for complex queries"
            ],
            "learning_progress": {
                "new_patterns_discovered": stats["user_patterns"]["unique_intents"],
                "knowledge_base_growth": len(stats["semantic_categories"])
            }
        }
        
        return reflection

    def set_confirmation_callback(self, callback):
        """Set callback function for user confirmation"""
        self.confirmation_callback = callback
    
    def needs_confirmation(self, tool_name: str, parameters: dict) -> bool:
        """Check if a tool call needs user confirmation"""
        operation = parameters.get('operation')
        return (tool_name in self.sensitive_operations and 
                operation in self.sensitive_operations[tool_name])
    
    def request_confirmation(self, tool_name: str, parameters: dict) -> str:
        """Generate confirmation request message"""
        operation = parameters.get('operation', 'unknown')
        
        if tool_name == 'email' and operation == 'send_email':
            recipient = parameters.get('recipient', 'unknown recipient')
            subject = parameters.get('subject', 'No Subject')
            body = parameters.get('body', '')
            
            # Show full body if it's short, otherwise show preview
            if len(body) <= 200:
                body_display = body
            else:
                body_display = body[:200] + '\n\n[Content truncated - full email is longer]'
            
            return f"""📧 Email Confirmation Required

I'm about to send an email with the following details:

📨 To: {recipient}
📋 Subject: {subject}
📝 Body:
{body_display}

Do you want me to proceed? (yes/y to confirm, no/n to cancel)"""

        elif tool_name == 'calendar':
            if operation == 'create_event':
                title = parameters.get('title', 'Untitled Event')
                return f"""📅 Calendar Event Confirmation

I'm about to create a calendar event:
• Title: {title}
• Start: {parameters.get('start_time', 'Not specified')}
• End: {parameters.get('end_time', 'Not specified')}

Do you want me to proceed? (yes/y to confirm, no/n to cancel)"""
            
            elif operation == 'delete_event':
                event_id = parameters.get('event_id', 'unknown')
                event_title = parameters.get('title', 'Unknown Event')
                
                # Try to get a more meaningful description
                if event_title != 'Unknown Event':
                    event_description = f'"{event_title}" (ID: {event_id})'
                else:
                    event_description = f'Event ID: {event_id}'
                
                return f"""🗑️ Delete Event Confirmation

I'm about to delete calendar event: {event_description}

Do you want me to proceed? (yes/y to confirm, no/n to cancel)"""
        
        elif tool_name == 'todo_list':
            if operation == 'delete_task':
                task_id = parameters.get('task_id', 'unknown')
                return f"""🗑️ Delete Task Confirmation

I'm about to delete task: {task_id}

Do you want me to proceed? (yes/y to confirm, no/n to cancel)"""
        
        # Generic confirmation
        return f"""⚠️ Confirmation Required

I'm about to execute: {tool_name} - {operation}

Do you want me to proceed? (yes/y to confirm, no/n to cancel)"""
    
    def handle_confirmation_response(self, response: str) -> str:
        """Handle user's confirmation response"""
        if not self.pending_confirmation:
            return "No pending action to confirm."
        
        response_lower = response.lower().strip()
        confirmed = response_lower in ['yes', 'y', '是', '确认', 'confirm', 'ok']
        
        if confirmed:
            # Execute the pending action
            tool_name = self.pending_confirmation['tool_name']
            parameters = self.pending_confirmation['parameters']
            
            logging.debug(f"User confirmed. Executing {tool_name}...")
            result = self.action_executor.execute_action(tool_name, parameters)
            
            # Clear pending confirmation
            self.pending_confirmation = None
            
            if result.get('status') == 'success':
                return f"✅ {result.get('result', 'Operation completed successfully')}"
            else:
                return f"❌ Operation failed: {result.get('error_message', 'Unknown error')}"
        else:
            # User cancelled
            self.pending_confirmation = None
            return "❌ Operation cancelled by user."
    
    def has_pending_confirmation(self) -> bool:
        """Check if there's a pending confirmation"""
        return self.pending_confirmation is not None
    
    def get_pending_confirmation_requests(self) -> list:
        """Get list of pending confirmation requests"""
        if self.pending_confirmation:
            return [{
                'id': 'current',
                'query': self.pending_confirmation.get('query', 'Unknown'),
                'tool_name': self.pending_confirmation['tool_name'],
                'operation': self.pending_confirmation['parameters'].get('operation', 'unknown'),
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(minutes=30)).isoformat()
            }]
        return []
    
    def cancel_confirmation_request(self, request_id: str):
        """Cancel a specific confirmation request"""
        if request_id == 'current' and self.pending_confirmation:
            self.pending_confirmation = None
            return True
        return False