import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'emobot')))

from emobot.agent.demo_manager import DemoManager
from emobot.agent.reasoning import ReasoningModule

def verify_scene_1():
    demo_manager = DemoManager()
    # Mock reasoning module
    reasoning_module = ReasoningModule()
    reasoning_module.demo_manager = demo_manager
    
    # Test Scene 1 trigger
    query = "handle the meeting request from Professor Tan"
    result = demo_manager.execute_demo_scenario(query, reasoning_module)
    
    print(f"Query: {query}")
    print(f"Response: {result.get('response')}")
    
    expected_response = "Sure, I'll coordinate your email and calendar for this. Based on the schedule, Tuesday 2:00-2:30 PM (after class) and Wednesday 3:00-3:30 PM (after workshop) or 4:00-4:30 PM are good slots. Would you like me to draft an English reply email to Professor Tan using these options?"
    
    if result.get('response') == expected_response:
        print("✅ Response verification PASSED")
    else:
        print(f"❌ Response verification FAILED.")
        print(f"Expected: {expected_response}")
        print(f"Got:      {result.get('response')}")

if __name__ == "__main__":
    verify_scene_1()
