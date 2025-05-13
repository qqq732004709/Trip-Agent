import json
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, END
from agent.intent_agent import intent_agent
from agent.clarify_agent import clarify_agent
from agent.itinerary_agent import itinerary_agent
from graph.state import AgentState
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AIMessage


def start(state: AgentState) -> AgentState:
    """Initialize the workflow with the input message."""
    return state


def human_input_node(state: AgentState) -> AgentState:
    """
    这个节点表示等待用户输入的状态。
    在图中使用这个节点可以明确表示流程在等待用户回复。
    
    Args:
        state: 当前的代理状态
    
    Returns:
        返回相同的状态，因为实际的用户输入是在外部处理的
    """
    # 这个节点不做任何操作，只起到标记用户输入点的作用
    # 真正的用户输入处理是在cli_main.py或者其他调用者中完成
    return state


def intent_router(state: AgentState) -> str:
    """
    路由决策函数，根据状态决定下一步走向
    - 如果需要澄清，转到澄清智能体
    - 如果信息已完整，转到行程规划智能体

    Args:
        state: 当前的代理状态

    Returns:
        str: 下一个节点名称或END标记
    """
    needs_clarification = state["metadata"].get("needs_clarification", False)
    
    # 根据 needs_clarification 标记决定下一步
    if needs_clarification:
        return "clarify_agent"
    else:
        return "itinerary_agent"


def clarify_router(state: AgentState) -> str:
    """
    澄清智能体路由函数
    - 如果还需要继续澄清，转到等待用户输入的节点
    - 如果澄清完成，回到意图理解智能体重新处理

    Args:
        state: 当前的代理状态

    Returns:
        str: 下一个节点名称
    """
    needs_clarification = state["metadata"].get("needs_clarification", False)
    
    if needs_clarification:
        return "human_input_node"  # 转到等待用户输入的节点，而不是终止流程
    else:
        return "intent_agent"  # 回到意图智能体重新处理


def get_runnable(checkpoint_path: str = None):
    """
    构建并返回已编译的 LangGraph 流程。
    可以通过传入 SQLite 路径实现持久化状态保存。

    Args:
        checkpoint_path: SQLite 数据库路径，用于持久化状态

    Returns:
        已编译的工作流对象
    """
    # 设置持久化配置
    config = {}
    if checkpoint_path:
        config["checkpointer"] = SqliteSaver(checkpoint_path)

    workflow = StateGraph(AgentState, **config)

    # 节点定义
    workflow.add_node("start_node", start)
    workflow.add_node("intent_agent", intent_agent)
    workflow.add_node("clarify_agent", clarify_agent)
    workflow.add_node("itinerary_agent", itinerary_agent)
    workflow.add_node("human_input_node", human_input_node)  # 添加人工输入节点

    # 流转逻辑
    workflow.add_edge("start_node", "intent_agent")
    workflow.add_conditional_edges("intent_agent", intent_router)
    workflow.add_conditional_edges("clarify_agent", clarify_router)
    workflow.add_edge("human_input_node", END)  # 人工输入后暂时结束当前流程，等待外部输入
    workflow.add_edge("itinerary_agent", END)  # Always end after itinerary_agent

    workflow.set_entry_point("start_node")

    return workflow.compile()
