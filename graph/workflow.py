# graph/workflow.py

from langgraph.graph import StateGraph, END
from agent.intent_agent import intent_agent
from graph.state import AgentState
from agent.itinerary_agent import itinerary_agent
from langgraph.checkpoint.sqlite import SqliteSaver

def start(state: AgentState):
    """Initialize the workflow with the input message."""
    return state

def get_runnable():
    """
    构建并返回已编译的 LangGraph 流程。
    可以通过传入 SQLite 路径实现持久化状态保存。
    """
    workflow = StateGraph(AgentState)

    # 节点定义
    workflow.add_node("start_node", start)
    workflow.add_node("intent_agent", intent_agent)
    workflow.add_node("itinerary_agent", itinerary_agent)

    # 流转逻辑
    workflow.add_edge("start_node", "intent_agent")
    workflow.add_edge("intent_agent", "itinerary_agent")
    workflow.add_edge("itinerary_agent", END)

    workflow.set_entry_point("start_node")

    return workflow.compile()
