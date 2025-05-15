# cli_main.py

from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage, AIMessage
from src.utils.model_selector import select_model
from colorama import Fore, Style

# Import functions for running workflow
from src.graph.builder import build_graph

# 调试用：加载 .env 文件
load_dotenv()

def main():
    # CLI 模式选择模型
    model_name, model_provider = select_model(mode="cli")
    
    # 获取用户输入
    print("\n请输入旅行需求，例如：我想去杭州玩三天，喜欢美食和古镇")
    user_input = input("旅行需求： ").strip()
    if not user_input:
        # 使用调试样例
        user_input = "我想去广州玩三天，喜欢美食和广州塔还有长隆动物园"
        print(f"{Fore.YELLOW}使用默认示例：{user_input}{Style.RESET_ALL}")

    # 构建初始状态
    state = {
        "messages": [
            HumanMessage(content=user_input)
        ],
        "data": {},
        "metadata": {
            "model_name": model_name,
            "model_provider": model_provider
        }
    }

    # 获取可运行的工作流
    runnable = build_graph()
    
    # 运行多轮对话流程
    max_turns = 10  # 最大轮次以允许足够的澄清问题
    current_turn = 0
    last_clarify_field = None
    
    while current_turn < max_turns:
        # 运行一步工作流
        result = runnable.invoke(state)
        
        # 获取最新状态
        needs_clarification = result["metadata"].get("needs_clarification", False)
        clarify_field = result["metadata"].get("clarify_field")
        
        # 如果有 itinerary_markdown，表示已完成，可以退出循环
        if "itinerary_markdown" in result.get("data", {}):
            break
            
        # 如果需要澄清，获取用户输入
        if needs_clarification:
            # 找到最后一条 AI 消消息作为问题
            all_messages = result["messages"]
            ai_messages = [m for m in all_messages if isinstance(m, AIMessage)]
            
            if ai_messages:
                clarify_question = ai_messages[-1].content
                print(f"\n{Fore.CYAN}AI问题：{clarify_question}{Style.RESET_ALL}")
                
                try:
                    user_response = input(f"{Fore.GREEN}您的回答：{Style.RESET_ALL}")
                    if not user_response.strip():
                        user_response = "均衡"  # 提供一个默认回答，防止空输入
                        print(f"{Fore.YELLOW}使用默认回答：{user_response}{Style.RESET_ALL}")
                except EOFError:
                    # 处理 EOF 错误 (Ctrl+D)
                    user_response = "均衡"
                    print(f"{Fore.YELLOW}检测到输入中断，使用默认回答：{user_response}{Style.RESET_ALL}")
                
                # 将用户回答添加到消息列表
                new_message = HumanMessage(content=user_response)
                
                # 更新状态 - 保存用户响应到相应的字段
                if clarify_field and clarify_field != last_clarify_field:
                    # 记录当前处理的澄清字段，避免重复处理
                    last_clarify_field = clarify_field
                    
                    # 如果有明确的需要澄清的字段，将用户回答保存到该字段
                    data = result.get("data", {})
                    if clarify_field in data:
                        # 确保回答格式符合字段要求
                        if clarify_field == "activity_preferences" and not isinstance(data[clarify_field], list):
                            data[clarify_field] = [user_response]
                        elif clarify_field == "activity_preferences" and isinstance(data[clarify_field], list):
                            data[clarify_field].append(user_response)
                        else:
                            data[clarify_field] = user_response
                        
                        print(f"{Fore.GREEN}已更新字段 {clarify_field}: {user_response}{Style.RESET_ALL}")
                
                # 更新状态 - 只替换消息，保留元数据和数据
                state = {
                    "messages": result["messages"] + [new_message],
                    "data": result.get("data", {}),
                    "metadata": result.get("metadata", {})
                }
                current_turn += 1
                continue
            else:
                # 如果没有找到 AI 消息，打印可用的消息类型以帮助调试
                message_types = [f"{type(m).__name__}" for m in all_messages]
                print(f"{Fore.RED}警告：找不到 AI 消息进行澄清。可用消息类型：{', '.join(message_types)}{Style.RESET_ALL}")
                break
        else:
            # 如果不需要澄清但也没有行程，可能是遇到了其他情况
            if "itinerary_markdown" not in result.get("data", {}):
                # 显示最后一条消息，如果有的话
                if result.get("messages"):
                    last_message = result["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        print(f"\n{Fore.CYAN}AI回复：{last_message.content}{Style.RESET_ALL}")
            break
    
    # 检查是否是因为达到最大轮次而退出
    if current_turn >= max_turns:
        print(f"\n{Fore.YELLOW}达到最大交互轮次 ({max_turns})，使用当前收集的信息生成行程。{Style.RESET_ALL}")
    
    # 输出行程 Markdown（如果有）
    itinerary_markdown = result["data"].get("itinerary_markdown", "⚠️ 未生成行程")
    print("\n🧳 生成的旅行行程 Markdown：\n")
    print(itinerary_markdown)


if __name__ == "__main__":
    main()
