from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.graph.state import AgentState


def _build_base_graph():
    """Build and return the base agent workflow graph."""
    builder = StateGraph(AgentState)
    builder.add_edge(START, "coordinator")
    builder.add_edge("coordinator", END)
    return builder

def build_graph():
    """Build and return the agent workflow graph without memory."""
    # build state graph
    builder = _build_base_graph()
    return builder.compile()


def build_graph_with_memory():
    """Build and return the agent workflow graph with memory."""
    # use persistent memory to save conversation history
    # TODO: be compatible with SQLite / PostgreSQL
    memory = MemorySaver()

    # build state graph
    builder = _build_base_graph()
    return builder.compile(checkpointer=memory)

graph = build_graph()