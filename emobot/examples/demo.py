"""
Emobot 使用示例

这个脚本演示了如何程序化地使用 Emobot agent，
而不是通过交互式命令行界面。
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.reasoning import ReasoningModule
from agent.memory import MemoryManager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

def demo_basic_conversation():
    """演示基本对话功能"""
    print("=== 基本对话演示 ===\n")
    
    # 初始化 agent（假设 MCP 服务器已经在运行）
    agent = ReasoningModule(
        model_id="gpt-4",
        server_url="http://127.0.0.1:8080",
        system_prompt_path="../configs/system_prompt.md"
    )
    
    # 测试查询
    queries = [
        "你好，请介绍一下你自己",
        "帮我搜索一下 Python 异步编程的最佳实践",
        "添加一个任务：学习 smolagents 框架",
        "显示我的待办事项"
    ]
    
    for query in queries:
        print(f"用户: {query}")
        response = agent.process_query(query)
        print(f"Emobot: {response}\n")
        print("-" * 50 + "\n")

def demo_memory_system():
    """演示记忆系统功能"""
    print("=== 记忆系统演示 ===\n")
    
    # 创建记忆管理器
    memory = MemoryManager()
    
    # 添加一些交互到短期记忆
    interactions = [
        {"user_input": "搜索机器学习资料", "intent": "search"},
        {"user_input": "发送邮件给张三", "intent": "email"},
        {"user_input": "添加任务：完成项目报告", "intent": "todo"}
    ]
    
    for interaction in interactions:
        memory.add_to_short_term(interaction)
    
    # 显示用户偏好分析
    preferences = memory.get_user_preferences()
    print("用户偏好分析:")
    print(f"最常用意图: {preferences['most_used_intents']}")
    print(f"活跃时段: {preferences['active_hours']}")
    
    # 保存重要的交互片段
    important_episode = {
        "query": "帮我制定一个学习计划",
        "response": "好的，我为您制定了一个详细的学习计划...",
        "importance": 0.9
    }
    memory.save_important_episode(important_episode)
    
    # 搜索相似的历史交互
    similar = memory.search_similar_episodes("学习")
    print(f"\n找到 {len(similar)} 个相关的历史交互")

def demo_advanced_reasoning():
    """演示高级推理功能"""
    print("=== 高级推理演示 ===\n")
    
    agent = ReasoningModule(
        model_id="gpt-4",
        server_url="http://127.0.0.1:8080"
    )
    
    # 复杂的多步骤任务
    complex_query = """
    请帮我完成以下任务：
    1. 搜索最新的 AI 发展趋势
    2. 基于搜索结果，创建一个学习待办清单
    3. 查看我的收件箱是否有相关邮件
    """
    
    print(f"复杂查询: {complex_query}")
    response = agent.process_query(complex_query)
    print(f"Emobot 响应: {response}")
    
    # 解释推理过程
    print("\n推理过程解释:")
    explanation = agent.explain_reasoning(complex_query)
    print(explanation)
    
    # 性能反思
    print("\n性能反思:")
    reflection = agent.reflect_on_performance()
    print(f"总交互次数: {reflection['interaction_count']}")
    print(f"改进建议: {reflection['improvement_suggestions']}")

def demo_custom_tools():
    """演示如何使用自定义工具"""
    print("=== 自定义工具演示 ===\n")
    
    # 这里展示如何注册自定义结果处理器
    from agent.actions import ActionExecutor
    
    executor = ActionExecutor("http://127.0.0.1:8080")
    
    # 定义自定义处理器
    def custom_processor(result):
        """自定义结果处理器示例"""
        if result.get("status") == "success":
            result["custom_field"] = "这是自定义处理添加的字段"
        return result
    
    # 注册处理器
    executor.register_result_processor("my_custom_tool", custom_processor)
    
    print("已注册自定义工具处理器")
    
    # 获取执行统计
    stats = executor.get_execution_stats()
    print(f"执行统计: {stats}")

def main():
    """主函数"""
    print("🤖 Emobot 功能演示\n")
    
    demos = [
        ("基本对话", demo_basic_conversation),
        ("记忆系统", demo_memory_system),
        ("高级推理", demo_advanced_reasoning),
        ("自定义工具", demo_custom_tools)
    ]
    
    print("请选择要演示的功能:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (0-4): ")
            choice = int(choice)
            
            if choice == 0:
                print("退出演示")
                break
            elif 1 <= choice <= len(demos):
                print("\n")
                demos[choice-1][1]()
                print("\n" + "="*50 + "\n")
            else:
                print("无效选择，请重试")
                
        except ValueError:
            print("请输入数字")
        except KeyboardInterrupt:
            print("\n退出演示")
            break
        except Exception as e:
            print(f"演示过程中出错: {e}")

if __name__ == "__main__":
    # 提示：确保 MCP 服务器正在运行
    print("⚠️  注意：运行此演示前，请确保 MCP 工具服务器已经启动")
    print("可以在另一个终端运行: python main.py\n")
    
    main() 