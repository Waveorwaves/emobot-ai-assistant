"""
Reasoning Wrapper for Web Application
Provides additional functionality for web interface integration
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .reasoning import ReasoningModule

class ReasoningWrapper:
    """
    Wrapper around ReasoningModule to provide web-friendly interfaces
    Adds step-by-step reasoning capture and structured responses
    """
    
    def __init__(self, reasoning_module: ReasoningModule):
        """
        Initialize reasoning wrapper
        
        Args:
            reasoning_module: The core reasoning module to wrap
        """
        self.reasoning_module = reasoning_module
        self.logger = logging.getLogger(__name__)
        self.current_steps = []
        
    def process_query_with_steps(self, query: str) -> Dict[str, Any]:
        """
        Process query and capture reasoning steps for web interface
        
        Args:
            query: User query string
            
        Returns:
            Dict containing response and reasoning steps
        """
        self.current_steps = []
        
        try:
            # Capture the agent's actual reasoning by intercepting the run method
            import sys
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            # Capture stdout to parse reasoning steps
            captured_output = io.StringIO()
            
            # Check for pending confirmation
            if self.reasoning_module.has_pending_confirmation():
                self._add_step("confirmation", "Handling confirmation response", {"query": query})
                result = self.reasoning_module.handle_confirmation_response(query)
            else:
                # Get response from reasoning module
                result = self.reasoning_module.process_query(query)
            
            # Handle both string and dict responses
            response_text = ""
            ui_action = None
            
            if isinstance(result, dict):
                response_text = result.get("response", "")
                ui_action = result.get("ui_action")
            else:
                response_text = str(result)
            
            # Get reasoning steps
            steps = self.reasoning_module.get_last_reasoning_steps()
            
            # If we captured actual steps, use them
            if steps:
                self.current_steps = steps
            # If no steps were captured, add generic ones
            elif len(self.current_steps) == 0:
                self.logger.warning("Falling back to generic steps")
                self._add_step("input", "Processing user query", {"query": query})
                self._add_step("reasoning", "Analyzing query and planning actions")
                self._add_step("output", "Generated response", {"response": response_text})
            
            return {
                'success': True,
                'response': response_text,
                'ui_action': ui_action,
                'reasoning_steps': self.current_steps,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            self._add_step("error", f"Error occurred: {str(e)}")
            
            return {
                'success': False,
                'response': f"Sorry, I encountered an error: {str(e)}",
                'error': str(e),
                'reasoning_steps': self.current_steps,
                'timestamp': datetime.now().isoformat()
            }
    
    def _parse_agent_output(self, output: str, query: str, response: str):
        """
        Parse agent output to extract reasoning steps
        
        Args:
            output: Captured stdout from agent
            query: Original user query
            response: Final response
        """
        if not output or len(output) < 10:
            self.logger.warning("No output captured from agent")
            return
            
        lines = output.split('\n')
        step_num = 1
        current_block = []
        current_type = None
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Detect step type markers
            if '**Thought**:' in line_stripped or 'Thought:' in line_stripped or line_stripped.startswith('Thinking'):
                if current_block and current_type:
                    self._add_step_simple(step_num, current_type, current_type.title(), ' '.join(current_block))
                    step_num += 1
                current_type = "thought"
                current_block = [line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else line_stripped]
                
            elif '**Action**:' in line_stripped or 'Action:' in line_stripped:
                if current_block and current_type:
                    self._add_step_simple(step_num, current_type, current_type.title(), ' '.join(current_block))
                    step_num += 1
                current_type = "tool_call"
                current_block = [line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else line_stripped]
                
            elif '**Observation**:' in line_stripped or 'Observation:' in line_stripped:
                if current_block and current_type:
                    self._add_step_simple(step_num, current_type, current_type.title(), ' '.join(current_block))
                    step_num += 1
                current_type = "observation"
                current_block = [line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else line_stripped]
                
            elif 'Final Answer:' in line_stripped:
                if current_block and current_type:
                    self._add_step_simple(step_num, current_type, current_type.title(), ' '.join(current_block))
                    step_num += 1
                answer = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else response
                self._add_step_simple(step_num, "final_answer", "Final Answer", answer)
                step_num += 1
                current_block = []
                current_type = None
            else:
                # Continue building current block
                if current_type:
                    current_block.append(line_stripped)
        
        # Add any remaining block
        if current_block and current_type:
            self._add_step_simple(step_num, current_type, current_type.title(), ' '.join(current_block))
        
        self.logger.info(f"Parsed {len(self.current_steps)} reasoning steps from output")
    
    def _add_step_simple(self, step_num: int, step_type: str, action: str, reasoning: str):
        """
        Add a simple reasoning step
        
        Args:
            step_num: Step number
            step_type: Type of step
            action: Action description
            reasoning: Reasoning text
        """
        step = {
            'step': step_num,
            'type': step_type,
            'action': action,
            'reasoning': reasoning,
            'confidence': 0.8,
            'timestamp': datetime.now().isoformat()
        }
        self.current_steps.append(step)
        self.logger.debug(f"Added reasoning step: {step}")
    
    def _add_step(self, step_type: str, message: str, data: Optional[Dict] = None):
        """
        Add a reasoning step for web interface display
        
        Args:
            step_type: Type of step (input, reasoning, action, output, error)
            message: Human-readable message
            data: Optional additional data
        """
        step = {
            'step': len(self.current_steps) + 1,
            'type': step_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if data:
            step['data'] = data
            
        self.current_steps.append(step)
        self.logger.debug(f"Added reasoning step: {step}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools in web-friendly format
        
        Returns:
            List of tool descriptions
        """
        try:
            return self.reasoning_module.action_executor.get_available_tools()
        except Exception as e:
            self.logger.error(f"Error getting tools: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics for web interface
        
        Returns:
            Memory statistics dictionary
        """
        try:
            return self.reasoning_module.memory.get_memory_stats()
        except Exception as e:
            self.logger.error(f"Error getting memory stats: {e}")
            return {}
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics for web interface
        
        Returns:
            Execution statistics dictionary
        """
        try:
            return self.reasoning_module.action_executor.get_execution_stats()
        except Exception as e:
            self.logger.error(f"Error getting execution stats: {e}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for web interface
        
        Returns:
            Health status dictionary
        """
        try:
            return self.reasoning_module.action_executor.health_check()
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def has_pending_confirmation(self) -> bool:
        """
        Check if there are pending confirmation requests
        
        Returns:
            True if there are pending confirmations
        """
        try:
            return self.reasoning_module.has_pending_confirmation()
        except Exception as e:
            self.logger.error(f"Error checking pending confirmations: {e}")
            return False
    
    def get_pending_confirmations(self) -> List[Dict[str, Any]]:
        """
        Get pending confirmation requests for web interface
        
        Returns:
            List of pending confirmation requests
        """
        try:
            return self.reasoning_module.get_pending_confirmation_requests()
        except Exception as e:
            self.logger.error(f"Error getting pending confirmations: {e}")
            return []
    
    def cancel_all_confirmations(self) -> Dict[str, Any]:
        """
        Cancel all pending confirmation requests
        
        Returns:
            Result of cancellation operation
        """
        try:
            pending = self.get_pending_confirmations()
            cancelled_count = 0
            
            for req in pending:
                self.reasoning_module.cancel_confirmation_request(req['id'])
                cancelled_count += 1
            
            return {
                'success': True,
                'cancelled_count': cancelled_count,
                'message': f'Cancelled {cancelled_count} pending confirmations'
            }
            
        except Exception as e:
            self.logger.error(f"Error cancelling confirmations: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to cancel confirmations'
            }
