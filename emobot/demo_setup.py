import os
import shutil
import json

def setup_demo():
    """
    Setup demo data for Emobot scenario.
    Copies seed data to active memory files.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    demo_data_dir = os.path.join(base_dir, "demo_data")
    agent_memory_dir = os.path.join(base_dir, "agent_memory")
    
    # Ensure directories exist
    os.makedirs(agent_memory_dir, exist_ok=True)
    
    print("🚀 Setting up Emobot Demo Environment...")
    
    # 1. Setup Calendar
    calendar_src = os.path.join(demo_data_dir, "calendar.json")
    calendar_dst = os.path.join(agent_memory_dir, "calendar_events.json")
    if os.path.exists(calendar_src):
        shutil.copy2(calendar_src, calendar_dst)
        print(f"✅ Calendar data seeded to {calendar_dst}")
    else:
        print(f"❌ Calendar demo data not found at {calendar_src}")

    # 2. Setup Todos
    # Note: TodoListManager defaults to "todo_list.json" in current dir
    todo_src = os.path.join(demo_data_dir, "todos.json")
    todo_dst = os.path.join(base_dir, "todo_list.json")
    if os.path.exists(todo_src):
        shutil.copy2(todo_src, todo_dst)
        print(f"✅ Todo data seeded to {todo_dst}")
    else:
        print(f"❌ Todo demo data not found at {todo_src}")

    # 3. Setup Profile (Optional - reset to default)
    # ProfileManager handles default if file missing, but we can force a clean slate
    profile_path = os.path.join(agent_memory_dir, "user_profile.json")
    if os.path.exists(profile_path):
        # backup existing profile
        shutil.copy2(profile_path, profile_path + ".bak")
        print(f"ℹ️  Existing profile backed up to {profile_path}.bak")
        
        # Remove it to force default load or we could seed a specific profile
        # os.remove(profile_path) 
        # print("✅ Profile reset to defaults")
    
    print("\n🎉 Demo Setup Complete!")
    print("You can now start the web app with: python emobot/web_app.py")
    print("And enable demo mode via the API or UI.")

if __name__ == "__main__":
    setup_demo()
