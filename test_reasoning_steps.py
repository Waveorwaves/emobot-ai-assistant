#!/usr/bin/env python3
"""
Test script to verify reasoning steps are being captured
"""

import sys
import os
import json

# Add the emobot directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'emobot'))

from agent.reasoning import ReasoningModule
from agent.reasoning_wrapper import ReasoningWrapper

def test_reasoning_steps():
    """Test that reasoning steps are captured"""
    print("🧪 Testing Reasoning Steps Capture\n")
    
    try:
        # Initialize reasoning module
        print("1. Initializing reasoning module...")
        reasoning_module = ReasoningModule(
            model_id="gemini-2.5-flash",
            server_url="http://127.0.0.1:8080",
            use_local_model=False
        )
        print("✅ Reasoning module initialized\n")
        
        # Create wrapper
        print("2. Creating reasoning wrapper...")
        wrapper = ReasoningWrapper(reasoning_module)
        print("✅ Wrapper created\n")
        
        # Test query
        test_query = "What is 2+2?"
        print(f"3. Processing test query: '{test_query}'")
        result = wrapper.process_query_with_steps(test_query)
        
        print("\n📊 Results:")
        print(f"Success: {result['success']}")
        print(f"Response: {result['response'][:100]}...")
        print(f"\n🔍 Reasoning Steps ({len(result['reasoning_steps'])} total):")
        
        for step in result['reasoning_steps']:
            print(f"\n  Step {step['step']}: {step['type'].upper()}")
            print(f"    Action: {step['action']}")
            print(f"    Reasoning: {step['reasoning'][:100]}...")
            print(f"    Confidence: {step['confidence']}")
            if step.get('tool_name'):
                print(f"    Tool: {step['tool_name']}")
        
        print("\n✅ Test completed successfully!")
        
        # Save to file for inspection
        with open('test_reasoning_output.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print("\n📝 Full output saved to test_reasoning_output.json")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_reasoning_steps()
    sys.exit(0 if success else 1)
