import sys
import os
import logging

# Add emobot1 to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from emobot.agent.reasoning import ReasoningModule

# Configure logging
logging.basicConfig(level=logging.INFO)

def verify_demo():
    print("🚀 Starting Hardcoded Demo Verification")
    
    try:
        # Initialize reasoning module
        agent = ReasoningModule(use_local_model=False)
        print("✅ Agent initialized")
        
        # Define test queries
        queries = [
            "Emobot, please help me handle the meeting request from Professor Tan",
            "Yes, please draft a polite English reply. Make Tuesday 2:00–2:30 PM the first choice",
            "Don’t send it yet. Please add a to-do",
            "Emobot, please show my current profile",
            "Please update my style with unfamiliar contacts to: friendly but still concise and professional",
            "Emobot, please write an English email to Professor Tan, updating him on the Emobot progress",
            "Great. Now please write an email to my mom in English.",
            "Now write an email to Alex Li in English.",
            "Emobot, please summarize the tone of these three emails",
            "Emobot, please show me today’s AI Insights",
            "Accept Insight 1 and Insight 2"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n--- Test Query {i}: {query[:50]}... ---")
            response = agent.process_query(query)
            print(f"Response length: {len(response)}")
            print(f"Response preview: {response[:100]}...")
            
            if "I'm sorry, I couldn't process" in response:
                print(f"❌ Failed to match query {i}")
            else:
                print(f"✅ Query {i} matched and processed")
                
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_demo()
