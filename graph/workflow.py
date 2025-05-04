# graph/workflow.py

from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agent.itinerary_agent import itinerary_agent
from langgraph.checkpoint.sqlite import SqliteSaver

def get_runnable(memory_path: str = ":memory:"):
    """
    构建并返回已编译的 LangGraph 流程。
    可以通过传入 SQLite 路径实现持久化状态保存。
    """
    workflow = StateGraph(AgentState)

    # 节点定义
    workflow.add_node("start_node", lambda state: state)
    workflow.add_node("itinerary_agent", itinerary_agent)

    # 流转逻辑
    workflow.add_edge("start_node", "itinerary_agent")
    workflow.add_edge("itinerary_agent", END)

    workflow.set_entry_point("start_node")

    memory = SqliteSaver.from_conn_string(memory_path)
    return workflow.compile(checkpointer=memory)
