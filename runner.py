# runner.py

from langchain_core.messages import HumanMessage
from src.graph.workflow import get_runnable
from colorama import Fore, Style

runnable = get_runnable()
def run_itinerary(input_text: str, model_name: str, model_provider: str):
    """
    构造 AgentState 并运行 itinerary agent 流程。
    """
    # 构建初始状态
    state = {
        "messages": [
            HumanMessage(content=input_text)
        ],
        "data": {
        },
        "metadata": {
            "model_name": model_name,
            "model_provider": model_provider
        }
    }

    # 执行流程
    result = runnable.invoke(state)

    # 返回行程单
    itinerary = result["data"].get("itinerary_markdown", "⚠️ 未生成行程")
    return itinerary