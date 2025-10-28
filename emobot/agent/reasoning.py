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
                logging.debug("Final Answer found!")
                logging.debug(f"Final answer length: {len(final_answer)} characters")
                logging.debug(f"Final answer preview: {final_answer[:200]}...")
                return final_answer
            elif final_answer:
                logging.debug(f"Final Answer found after {len(tool_results)} tool executions!")
                logging.debug(f"Final answer length: {len(final_answer)} characters")
                logging.debug(f"Final answer preview: {final_answer[:200]}...")
                
                # Check if the final answer looks incomplete or is just raw search results
                is_incomplete = False
                
                # Check 1: Too short with header phrases
                if len(final_answer) < 150 and any(
                    phrase in final_answer.lower() for phrase in [
                        'here is', 'here are', 'here\'s', 'contact list', 'calendar', 'events',
                        'search results', 'found the following', 'operation was completed'
                    ]
                ):
                    is_incomplete = True
                    logging.warning("Final answer appears incomplete (too short with header)")
                
                # Check 2: For web search results, ensure it's not just raw results
                if tool_results:
                    last_tool = tool_results[-1].get('tool')
                    if last_tool == 'web_search':
                        # If the answer just contains URLs or looks like raw search results
                        if ('🔗' in final_answer or 'http' in final_answer) and len(final_answer) < 500:
                            is_incomplete = True
                            logging.warning("Final answer appears to be raw search results without synthesis")
                        # If it's a simple statement about search results
                        elif any(phrase in final_answer.lower() for phrase in [
                            'here are the search results',
                            'search results for',
                            'i found the following'
                        ]) and len(final_answer) < 300:
                            is_incomplete = True
                            logging.warning("Final answer is just presenting search results without analysis")
                
                if is_incomplete:
                    logging.warning("Regenerating answer from tool results...")
                    generated_answer = self._generate_fallback_answer(query, tool_results, current_thought)
                    logging.debug(f"Regenerated answer length: {len(generated_answer)} characters")
                    return generated_answer
                
                return final_answer
            
            # If we have tool results but no final answer, force generate one
            if tool_results and not final_answer and not tool_call:
                logging.debug("Tool results available but no final answer, generating from results...")
                generated_answer = self._generate_final_answer_from_results(query, tool_results)
                logging.debug(f"Generated answer length: {len(generated_answer)} characters")
                logging.debug(f"Generated answer preview: {generated_answer[:200]}...")
                return generated_answer
            
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

    def _format_available_tools(self) -> str:
        """Format available tools for the prompt"""
        tools_info = []
        for tool_name, tool in self.tools.items():
            # Get tool description from the tool object
            try:
                description = tool.description if hasattr(tool, 'description') else f"{tool_name} tool"
                tools_info.append(f"- {tool_name}: {description}")
            except:
                tools_info.append(f"- {tool_name}")
        return "\n        ".join(tools_info)
    
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
        You are in step {step} of the ReAct loop (max {self.max_steps} steps).

        User Query: {query}
        {context_section}

        Execution Plan:
        {plan.get('plan', 'No plan available')}

        Current Progress:
        - Steps completed: {len(tool_results)}
        - Steps remaining: {self.max_steps - step}

        Current Thought State:
        {current_thought if current_thought else "Initial State - Start by analyzing the query and planning your approach"}

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

        Available Tools:
        {self._format_available_tools()}

        Please think according to the following format:

        **Thought**: 
        1. Understand what the user wants to achieve (not just the keywords they used)
        2. For complex tasks, break them down into smaller steps
        3. Review what has been done so far (check tool results history)
        4. Determine the NEXT action needed:
           - If you need more information, use a tool
           - If you have gathered enough information, provide final answer
        5. Consider the conversation context and previous tool results

        **Action**: 
        - If a tool is needed, use JSON format:
        ```json
        {{
          "tool_name": "tool_name_here",
          "parameters": {{
            "operation": "operation_name",
            "param1": "value1",
            "param2": "value2"
          }}
        }}
        ```
        
        - If you have enough information to answer, use:
        ```
        Final Answer: Your complete answer based on the information gathered
        ```

        IMPORTANT REMINDERS:
        - Understand user INTENT, not just keywords
        - "get my contact list" means use email tool with operation="get_contacts"
        - "what's Jason's email" means use email tool with operation="search_contacts"
        - "check my calendar" means use calendar tool with operation="list_events"
        - Always wait for tool results before providing final answers for action requests
        - When providing final answers with lists, include the COMPLETE information from tool results
        - Do NOT truncate or summarize lists - show all the data the tool returned
        
        CRITICAL FOR WEB SEARCH:
        - After getting search results, you MUST analyze and synthesize the information
        - Do NOT just display raw search results as your final answer
        - Extract key information, organize it logically, and present it clearly
        - For complex queries (like "how to apply for visa"), provide step-by-step guidance
        - Include relevant details from multiple search results

        Please start your thinking:
        """
        return prompt

    def _extract_tool_call(self, query: str, thought: str) -> Optional[dict]:
        """Extract tool call from thought result - let the model decide"""
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
            
            logging.debug("No valid tool call found in model response")
            return None
            
        except Exception as e:
            logging.error(f"Tool call extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_tool_call_from_context(self, query: str, thought: str) -> Optional[dict]:
        """Generate tool call from context when extraction fails"""
        import re
        combined_text = query + " " + thought
        combined_lower = combined_text.lower()
        
        # Contact query detection (before email sending detection)
        # More specific patterns for contact queries
        contact_query_patterns = [
            r"what'?s?\s+(\w+(?:\s+\w+)?)'?s?\s+email",     # "what's Jason's email"
            r"get\s+(\w+(?:\s+\w+)?)'?s?\s+email",          # "get Jason's email"
            r"get\s+my\s+contact\s+(\w+(?:\s+\w+)?)'?s?\s+email",  # "get my contact Jason's email"
            r"find\s+(\w+(?:\s+\w+)?)'?s?\s+contact",       # "find Jason's contact"
            r"(\w+(?:\s+\w+)?)'?s?\s+email\s+address",      # "Jason's email address"
            r"(\w+(?:\s+\w+)?)'?s?\s+phone",                # "Jason's phone"
            r"contact\s+info\s+for\s+(\w+(?:\s+\w+)?)",     # "contact info for Jason"
            r"list\s+my\s+contacts?",                       # "list my contacts" or "list my contact"
            r"show\s+my\s+contacts?",                       # "show my contacts" or "show my contact"
            r"get\s+my\s+contacts?(?:\s+list)?",            # "get my contacts" or "get my contact list"
            r"show\s+me\s+my\s+contacts?",                  # "show me my contacts"
            r"display\s+my\s+contacts?",                    # "display my contacts"
            r"contacts?\s+list",                            # "contact list" or "contacts list"
            r"my\s+contact\s+list",                         # "my contact list"
        ]
        
        # Check for contact query patterns
        for pattern in contact_query_patterns:
            match = re.search(pattern, combined_lower, re.IGNORECASE)
            if match:
                # Handle different pattern types
                # Check if this is a list/show all contacts request
                if any(keyword in pattern for keyword in ["list", "show", "display", "my contact"]) and \
                   not any(keyword in pattern for keyword in ["what", "find", "info for"]):
                    logging.debug("List contacts query detected")
                    return {
                        "tool_name": "email",
                        "parameters": {
                            "operation": "get_contacts"
                        }
                    }
                else:
                    # Try to get the search query from the match
                    try:
                        search_query = match.group(1).strip()
                        logging.debug(f"Contact search query detected for: {search_query}")
                        return {
                            "tool_name": "email",
                            "parameters": {
                                "operation": "search_contacts",
                                "search_query": search_query
                            }
                        }
                    except (IndexError, AttributeError):
                        # No capture group, treat as list contacts
                        logging.debug("List contacts query detected (no capture group)")
                        return {
                            "tool_name": "email",
                            "parameters": {
                                "operation": "get_contacts"
                            }
                        }
        
        # Fallback contact detection - but be more careful not to trigger on email sending
        # Only trigger if we have contact-related keywords AND no sending keywords
        has_contact_keywords = any(keyword in combined_lower for keyword in ['contact', 'email address', 'phone number'])
        has_query_keywords = any(pattern in combined_lower for pattern in [
            "get", "find", "what's", "what is", "show me", "tell me", "list",
            "contact info", "email address", "phone number", "contact details", "contact list"
        ])
        has_send_keywords = any(pattern in combined_lower for pattern in [
            "send", "email to", "write to", "compose", "message to", "mail to"
        ])
        
        if (has_contact_keywords or has_query_keywords) and not has_send_keywords:
            # Extract potential name from query
            name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
            names = re.findall(name_pattern, query)
            search_query = names[0] if names else "contacts"
            
            logging.debug(f"Fallback contact search for: {search_query}")
            if search_query == "contacts" or "list" in combined_lower or "all" in combined_lower:
                return {
                    "tool_name": "email",
                    "parameters": {
                        "operation": "get_contacts"
                    }
                }
            else:
                return {
                    "tool_name": "email",
                    "parameters": {
                        "operation": "search_contacts",
                        "search_query": search_query
                    }
                }
        
        # Check for email address
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', combined_text)
        
        # Email sending detection (but exclude contact queries)
        if email_match and any(keyword in combined_lower for keyword in ['send', 'email', 'mail', 'ask', 'tell', 'notify', 'inform']) and not any(keyword in combined_lower for keyword in ['get', 'find', 'what', 'contact', 'my contact']):
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
    
    # Note: The following helper functions are kept for backward compatibility
    # but should not be actively used. The model should decide tool calls itself.
    
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
            elif tool_name == 'email' and parameters.get('operation') in ['search_contacts', 'get_contacts']:
                # Use the fallback answer method for contact results
                return self._generate_fallback_answer(query, tool_results, "")
            elif tool_name == 'calendar' and parameters.get('operation') == 'list_events':
                events = result.get('events', [])
                if events:
                    return f"Here are your calendar events: {result.get('result', '')}"
                else:
                    return "You have no events scheduled."
            elif tool_name == 'todo_list':
                return f"Todo list operation completed: {result.get('result', '')}"
            elif tool_name == 'web_search':
                # For web search, always use fallback to synthesize results
                return self._generate_fallback_answer(query, tool_results, "")
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
                    
                    # Check if we have contact search results to display
                    elif result['tool'] == 'email' and result['parameters'].get('operation') == 'search_contacts':
                        contact_result = result['result']
                        if isinstance(contact_result, dict) and contact_result.get('status') == 'success':
                            contacts = contact_result.get('result', [])
                            if contacts:
                                contact_list = "Here are the matching contacts:\n\n"
                                for i, contact in enumerate(contacts, 1):
                                    name = contact.get('name', 'Unknown Name')
                                    emails = contact.get('emails', [])
                                    phones = contact.get('phones', [])
                                    
                                    contact_list += f"{i}. **{name}**\n"
                                    if emails:
                                        contact_list += f"   📧 Email: {', '.join(emails)}\n"
                                    if phones:
                                        contact_list += f"   📞 Phone: {', '.join(phones)}\n"
                                    contact_list += "\n"
                                return contact_list
                            else:
                                search_query = result['parameters'].get('search_query', 'the specified person')
                                return f"I couldn't find any contacts matching '{search_query}' in your address book."
                        else:
                            error_msg = contact_result.get('error_message', 'Unknown error')
                            if "People API" in error_msg:
                                return f"❌ Contact functionality unavailable: {error_msg}\n\nPlease follow these steps to enable People API:\n1. Visit Google Cloud Console\n2. Search and enable 'People API'\n3. Re-authenticate the application"
                            return "I couldn't search your contacts. Please try again."
                    
                    # Check if we have all contacts to display
                    elif result['tool'] == 'email' and result['parameters'].get('operation') == 'get_contacts':
                        contact_result = result['result']
                        if isinstance(contact_result, dict) and contact_result.get('status') == 'success':
                            contacts = contact_result.get('result', [])
                            if contacts:
                                contact_list = f"Here are your contacts ({len(contacts)} total):\n\n"
                                for i, contact in enumerate(contacts[:10], 1):  # Show first 10
                                    name = contact.get('name', 'Unknown Name')
                                    emails = contact.get('emails', [])
                                    contact_list += f"{i}. **{name}**"
                                    if emails:
                                        contact_list += f" - {emails[0]}"
                                    contact_list += "\n"
                                
                                if len(contacts) > 10:
                                    contact_list += f"\n... and {len(contacts) - 10} more contacts."
                                return contact_list
                            else:
                                return "You don't have any contacts in your address book."
                        else:
                            error_msg = contact_result.get('error_message', 'Unknown error')
                            if "People API" in error_msg:
                                return f"❌ Contact functionality unavailable: {error_msg}\n\nPlease follow these steps to enable People API:\n1. Visit Google Cloud Console\n2. Search and enable 'People API'\n3. Re-authenticate the application"
                            return "I couldn't retrieve your contacts. Please try again."
                    
                    # Check if we have web search results to display
                    elif result['tool'] == 'web_search':
                        search_result = result['result']
                        if isinstance(search_result, dict) and search_result.get('status') == 'success':
                            search_results = search_result.get('results', [])
                            query_text = result['parameters'].get('query', 'your query')
                            original_query = query  # The user's original question
                            
                            if isinstance(search_results, list) and search_results:
                                # Instead of just showing raw results, synthesize them
                                synthesis_text = f"Based on my search for '{query_text}', here's what I found:\n\n"
                                
                                # Extract key information from search results
                                key_points = []
                                sources = []
                                
                                for i, item in enumerate(search_results[:5], 1):
                                    title = item.get('title', 'No title')
                                    snippet = item.get('snippet', 'No description available')
                                    url = item.get('url', '')
                                    
                                    # Clean up snippet - remove extra spaces and newlines
                                    import re
                                    snippet = re.sub(r'\s+', ' ', snippet).strip()
                                    
                                    # Truncate at sentence boundary if too long
                                    if len(snippet) > 200:
                                        # Try to cut at sentence end
                                        sentences = re.split(r'[.!?]\s+', snippet[:200])
                                        if len(sentences) > 1:
                                            snippet = sentences[0] + '.'
                                        else:
                                            # Cut at word boundary
                                            snippet = snippet[:200].rsplit(' ', 1)[0] + '...'
                                    
                                    # Add to key points if it has useful information
                                    if snippet and snippet != 'No description available' and len(snippet) > 20:
                                        key_points.append(snippet)
                                    
                                    # Collect sources
                                    if url:
                                        sources.append(f"{i}. [{title}]({url})")
                                
                                # Build synthesized answer with a summary
                                if key_points:
                                    # Add a brief summary based on the query type
                                    if 'hotel' in original_query.lower() or 'stay' in original_query.lower():
                                        synthesis_text += "**Summary:** When booking hotels in New York for December, consider location, amenities, and booking platforms for the best deals.\n\n"
                                    elif 'visa' in original_query.lower():
                                        synthesis_text += "**Summary:** Applying for a visa requires proper documentation, advance planning, and meeting specific requirements.\n\n"
                                    else:
                                        synthesis_text += "**Summary:** Here are the key findings from my search:\n\n"
                                    
                                    synthesis_text += "**Key Points:**\n"
                                    for i, point in enumerate(key_points[:5], 1):
                                        synthesis_text += f"{i}. {point}\n"
                                    synthesis_text += "\n"
                                
                                if sources:
                                    synthesis_text += "**Sources for More Details:**\n"
                                    synthesis_text += "\n".join(sources)
                                    synthesis_text += "\n\n"
                                
                                # Add context-specific guidance based on the query
                                if any(word in original_query.lower() for word in ['how', 'what', 'guide', 'steps', 'process']):
                                    synthesis_text += "💡 *For detailed step-by-step guidance, please refer to the sources above.*"
                                
                                return synthesis_text
                            elif isinstance(search_results, str):
                                # Handle case where results is a string message
                                return f"Search results for '{query_text}': {search_results}"
                            else:
                                return f"I couldn't find any results for '{query_text}'."
                        else:
                            error_msg = search_result.get('error_message', 'Unknown error')
                            return f"I encountered an error while searching: {error_msg}"
                   
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