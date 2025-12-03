import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'emobot')))

from emobot.agent.demo_manager import DemoManager
from emobot.agent.reasoning import ReasoningModule

def verify_scene_3():
    demo_manager = DemoManager()
    # Mock reasoning module
    reasoning_module = ReasoningModule()
    reasoning_module.demo_manager = demo_manager
    
    # Test Scene 3 trigger
    query = "add a to-do: if I don’t get a reply within two days, remind me to follow up with Professor Tan"
    result = demo_manager.execute_demo_scenario(query, reasoning_module)
    
    print(f"Query: {query}")
    print(f"Response: {result.get('response')}")
    
    expected_response = "Okay, I’ll make sure this doesn’t fall through the cracks. ✅ The follow-up task has been created: **Title:** Follow up with Prof. Tan about Emobot meeting **Due:** In 2 days at 9:00 AM **Category:** Study **Notes:** Check if there is a reply from Professor Tan. If not, send a brief follow-up email. I’ll remind you in two days and automatically re-check your inbox at that time."
    
    if result.get('response') == expected_response:
        print("✅ Response verification PASSED")
    else:
        print(f"❌ Response verification FAILED.")
        print(f"Expected: {expected_response}")
        print(f"Got:      {result.get('response')}")

    # Verify action
    actions = result.get('actions', [])
    if actions and actions[0]['tool'] == 'todo_list' and actions[0]['parameters']['operation'] == 'add_task':
        print("✅ Action verification PASSED (todo_list add_task)")
        
        # Verify the task was actually added to the manager
        from emobot.tools.mcp_server.todo_models import TodoListManager
        manager = TodoListManager()
        tasks = manager.get_all_tasks()
        # Find the task we just added (by title) - get the last one
        target_title = "Follow up with Prof. Tan about Emobot meeting"
        found_task = None
        # Iterate in reverse to find the newest one
        for task in reversed(tasks):
            if task.title == target_title:
                found_task = task
                break
        
        if found_task:
            print(f"✅ Task found in manager: {found_task.title}")
            print(f"   Category: {found_task.category.value}")
            print(f"   Description: {found_task.description}")
            print(f"   Due Date: {found_task.due_date}")
            
            if found_task.category.value == 'study':
                print("✅ Category verification PASSED")
            else:
                print(f"❌ Category verification FAILED. Expected 'study', got '{found_task.category.value}'")
                
            if found_task.description:
                print("✅ Description verification PASSED")
            else:
                print("❌ Description verification FAILED (Empty description)")
        else:
            print("❌ Task NOT found in manager")
            
    else:
        print("❌ Action verification FAILED")
        print(f"Actions: {actions}")

if __name__ == "__main__":
    verify_scene_3()
