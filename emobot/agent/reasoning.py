import json
import logging
from datetime import datetime
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
                tools[tool_name] = MCPToolWrapper(self.action_executor)
            
            return tools
        except Exception as e:
            logging.error(f"Failed to initialize tools: {e}")
            return {}

    def process_query(self, query: str) -> str:
        """
        Process user query using ReAct loop

        Args:
            query: User's query

        Returns:
            Final response to user
        """
        # Update memory with new query
        self.memory.add_to_short_term({"user_input": query})
        
        # Create execution plan
        plan = self._create_execution_plan(query)
        
        # Execute ReAct loop
        result = self._run_tool_calling_loop(query, plan)
        
        # Update memory with result
        self.memory.save_important_episode({
            "query": query,
            "result": result,
            "plan": plan
        })
        
        return result

    def _create_execution_plan(self, query: str) -> dict:
        """
        Create execution plan for the query

        Args:
            query: User's query

        Returns:
            Execution plan dictionary
        """
        plan_prompt = f"""
        Create a detailed execution plan for the following query: "{query}"

        The plan should include:
        1. Task Analysis: What needs to be done
        2. Tool Selection: Which tools might be needed
        3. Execution Steps: Step-by-step approach
        4. Expected Results: What we expect to achieve

        Available tools: {list(self.tools.keys())}

        Please provide a structured plan.
        """
        
        try:
            # Use a simple model call to create plan
            response = self.agent.run(plan_prompt)
            return {
                "query": query,
                "plan": response,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            # Fallback to basic plan
            return {
                "query": query,
                "plan": f"Basic plan for: {query}",
                "created_at": datetime.now().isoformat(),
                "error": str(e)
            }

    def _run_tool_calling_loop(self, query: str, plan: dict) -> str:
        """
        Run the ReAct tool calling loop

        Args:
            query: User's query
            plan: Execution plan

        Returns:
            Final response
        """
        tool_results = []
        current_thought = ""
        step = 1
        
        while step <= self.max_steps:
            print(f"\n🔄 ReAct Step {step}/{self.max_steps}")
            
            # Build thought prompt
            thought_prompt = self._build_thought_prompt(query, step, current_thought, tool_results, plan)
            
            # Get model's thought
            try:
                thought_response = self.agent.run(thought_prompt)
                current_thought = str(thought_response)
                print(f"💭 Thought: {current_thought[:200]}...")
            except Exception as e:
                print(f"❌ Thought generation failed: {e}")
                break
            
            # Extract tool call or final answer
            tool_call = self._extract_tool_call(current_thought)
            final_answer = self._extract_final_answer(current_thought)
            
            if final_answer:
                print(f"✅ Final Answer found!")
                return final_answer
            
            if tool_call:
                print(f"🔧 Executing tool: {tool_call['tool_name']}")
                
                # Execute tool
                result = self.action_executor.execute_action(
                    tool_call['tool_name'], 
                    tool_call['parameters']
                )
                
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
                    print(f"✅ Tool result: {result_str[:200]}...")
                else:
                    error_msg = result.get('error_message', 'Unknown error')
                    print(f"❌ Tool failed: {error_msg}")
            else:
                print("⚠️ No tool call or final answer detected")
                break
            
            step += 1
        
        # If we reach here, generate fallback answer
        return self._generate_fallback_answer(query, tool_results, current_thought)

    def _build_thought_prompt(self, query: str, step: int, current_thought: str, 
                            tool_results: list, plan: dict) -> str:
        """Build thought prompt for current step"""
        prompt = f"""
        You are in step {step} of the ReAct loop.

        User Query: {query}

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

    def _extract_tool_call(self, thought: str) -> Optional[dict]:
        """Extract tool call from thought result"""
        try:
            import re
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            matches = re.findall(json_pattern, thought, re.DOTALL)
            
            if matches:
                for match in matches:
                    try:
                        tool_call = json.loads(match)
                        if "tool_name" in tool_call and "parameters" in tool_call:
                            return tool_call
                    except json.JSONDecodeError:
                        continue
            
            return None
            
        except Exception as e:
            print(f"❌ Tool call extraction failed: {e}")
            return None

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
            print(f"❌ Final answer extraction failed: {e}")
            return ""

    def _generate_fallback_answer(self, query: str, tool_results: list, last_thought: str) -> str:
        """Generate fallback answer"""
        try:
            fallback_prompt = f"""
            Based on the following information, generate a useful reply for the user:

            User Query: {query}

            Tool Call History:
            """
            
            if tool_results:
                for result in tool_results:
                    fallback_prompt += f"""
            - Tool: {result['tool']}
              Result: {str(result['result'])[:200]}...
            """
            else:
                fallback_prompt += "No tool calls were made.\n"
            
            fallback_prompt += f"""

            Last Thought: {last_thought}

            Please provide a useful reply, directly answering the user's question:
            """
            
            response = self.agent.run(fallback_prompt)
            return str(response)
            
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