import sys
import os
import logging
import time

# Add emobot1 to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from emobot.agent.reasoning import ReasoningModule

# Configure logging
logging.basicConfig(level=logging.INFO)

def verify_demo():
    print("🚀 Starting Enhanced Demo Verification")
    
    try:
        # Initialize reasoning module
        agent = ReasoningModule(use_local_model=False)
        print("✅ Agent initialized")
        
        # Define test queries
        queries = [
            "Emobot, please help me handle the meeting request from Professor Tan"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n--- Test Query {i}: {query[:50]}... ---")
            start_time = time.time()
            response = agent.process_query(query)
            duration = time.time() - start_time
            
            print(f"Response received in {duration:.2f} seconds")
            print(f"Response preview: {response[:100]}...")
            
            # Check reasoning steps
            if hasattr(agent, 'last_reasoning_steps') and agent.last_reasoning_steps:
                print(f"✅ Reasoning steps captured: {len(agent.last_reasoning_steps)}")
                for step in agent.last_reasoning_steps:
                    print(f"   - [{step['type']}] {step['action']}")
            else:
                print("❌ No reasoning steps captured")
                
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_demo()
