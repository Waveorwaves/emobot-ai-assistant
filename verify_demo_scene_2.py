import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'emobot')))

from emobot.agent.demo_manager import DemoManager
from emobot.agent.reasoning import ReasoningModule

def verify_scene_2():
    demo_manager = DemoManager()
    # Mock reasoning module
    reasoning_module = ReasoningModule()
    reasoning_module.demo_manager = demo_manager
    
    # Test Scene 2 trigger
    query = "draft reply email"
    result = demo_manager.execute_demo_scenario(query, reasoning_module)
    
    print(f"Query: {query}")
    print(f"Response: {result.get('response')}")
    print(f"UI Action: {result.get('ui_action')}")
    
    expected_response = "I have created an email."
    if result.get('response') == expected_response:
        print("✅ Response verification PASSED")
    else:
        print(f"❌ Response verification FAILED. Expected '{expected_response}', got '{result.get('response')}'")

    if result.get('ui_action') and result['ui_action']['type'] == 'open_email_draft':
        print("✅ UI Action verification PASSED")
    else:
        print("❌ UI Action verification FAILED")

if __name__ == "__main__":
    verify_scene_2()
