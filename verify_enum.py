from emobot.tools.mcp_server.todo_models import TaskCategory

try:
    cat = TaskCategory("study")
    print(f"Success: {cat} value={cat.value}")
except Exception as e:
    print(f"Error: {e}")

try:
    cat = TaskCategory("other")
    print(f"Success: {cat} value={cat.value}")
except Exception as e:
    print(f"Error: {e}")
