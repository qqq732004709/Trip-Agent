# runner.py

from langchain_core.messages import HumanMessage
from graph.workflow import get_runnable
from colorama import Fore, Style
from utils.progress import progress

def run_itinerary(input_text: str, model_name: str, model_provider: str):
    """
    构造 AgentState 并运行 itinerary agent 流程。
    """
    # 获取 runnable 流程
    runnable = get_runnable()

    progress().start()
    # 运行流程
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

    # 打印并返回行程单
    itinerary = result["data"].get("itinerary_markdown", "⚠️ 未生成行程")
    progress().stop()
    return itinerary