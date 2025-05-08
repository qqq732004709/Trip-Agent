from langgraph.graph import StateGraph, END
from agent.intent_agent import intent_agent
from graph.state import AgentState
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AIMessage

def start(state: AgentState):
    """Initialize the workflow with the input message."""
    return state

def intent_loop_router(state: AgentState) -> str:
    request = state.get("data", {}).get("travel_details", {})
    confirmed = request.get("confirmed", False)

    # 判断 human message 数量作为对话轮数
    messages = state.get("messages", [])
    message_count = len([m for m in messages if m.type == "human"])

    if confirmed or message_count >= 5:
        print("🧾 Final extracted request:", request)
        state["messages"].append(
            AIMessage(content=f"收到您的需求：\n```json\n{json.dumps(request, indent=2, ensure_ascii=False)}\n```\n感谢您提供的信息！")
        )
        return END

    return "intent_agent"

def get_runnable():
    """
    构建并返回已编译的 LangGraph 流程。
    可以通过传入 SQLite 路径实现持久化状态保存。
    """
    workflow = StateGraph(AgentState)

    # 节点定义
    workflow.add_node("start_node", start)
    workflow.add_node("intent_agent", intent_agent)

    # 流转逻辑
    workflow.add_edge("start_node", "intent_agent")
    workflow.add_conditional_edges("intent_agent", intent_loop_router)

    workflow.set_entry_point("start_node")

    return workflow.compile()
