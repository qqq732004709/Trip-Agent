from typing import List, Dict, Optional, Any

from langchain_core.messages import AIMessage, HumanMessage
from utils.llm import call_llm
from graph.state import AgentState
from schema.itinerary import ItineraryRequest, from_request_to_data
from utils.progress import progress


def intent_agent(state: AgentState) -> dict:
    """
    理解用户旅行意图，提取旅行需求信息
    
    Args:
        state: 当前代理状态
        
    Returns:
        更新后的状态
    """
    progress().update_status("intent_agent", "⏳ 尝试理解用户需求")

    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]

    # 将所有用户消息合并为完整对话
    full_conversation = "\n".join([
        m.content for m in state["messages"] if isinstance(m, HumanMessage)
    ])

    # 一次性解析意图 + 结构（严格遵守文档：只调用一次 LLM）
    extracted_dict = parse_user_input(full_conversation, model_name, model_provider)

    # 转换为 ItineraryRequest 对象以标准化处理
    extracted = ItineraryRequest(
        destination=extracted_dict.get("destination", ""),
        start_date=extracted_dict.get("start_date", ""),
        end_date=extracted_dict.get("end_date", ""),
        activity_preferences=extracted_dict.get("preferences", {}).get("activities", []),
        budget_level=map_budget_to_level(extracted_dict.get("preferences", {}).get("budget", "")),
        special_requests=[]
    )

    # 如果提取结果为空，说明没有旅行意图
    if not extracted.destination and not extracted.activity_preferences:
        progress().update_status("intent_agent", "⚠️ 似乎不是旅行相关意图，终止流程")
        return {
            "data": state["data"],
            "messages": [
                AIMessage(content="目前我专注于旅行相关的任务，例如安排行程、推荐景点等。如果您需要帮助，请告诉我有关您的旅行计划～")
            ]
        }

    # 检查缺失的必要字段
    missing_fields = get_missing_fields(extracted)

    # 转换为 ItineraryData 并写入状态
    itinerary_data = from_request_to_data(extracted)
    
    # 信息完整，确认并进入下一阶段
    if not missing_fields:
        progress().update_status("intent_agent", "✅ 已获取完整需求")
        return {
            "data": itinerary_data,
            "metadata": {"needs_clarification": False},
            "messages": [
                AIMessage(content="太好了，我已经获取了您的全部旅行需求，即将为您规划行程。")
            ]
        }
    # 信息不全，标记需要澄清并返回
    else:
        progress().update_status("intent_agent", "❓ 需求不完整，需要澄清")
        followup = generate_followup_question(missing_fields)
        return {
            "data": itinerary_data,
            "metadata": {"needs_clarification": True},
            "messages": [AIMessage(content=followup)]
        }


def parse_user_input(conversation: str, model_name: str, model_provider: str) -> dict:
    """
    解析用户输入，提取旅行意图
    
    Args:
        conversation: 用户对话内容
        model_name: 模型名称
        model_provider: 模型提供商
        
    Returns:
        提取的旅行信息字典
    """
    prompt = f'''
你是一个智能旅行助手，请阅读以下用户的完整对话记录。

你的任务是：
1. 判断用户是否表达了明确的旅行意图（如：旅游、出行、放松、去哪玩等）；
2. 如果有旅行意图，请提取旅行需求为结构化 JSON：
   - destination: 目的地
   - start_date: 出发日期（如 2025-06-01）
   - end_date: 返回日期（如 2025-06-04）
   - preferences: 用户偏好，包括 activities 和 budget

对话记录：
"""
{conversation}
"""

请严格输出 JSON 格式，不要添加任何额外解释，不要添加注释，结构如下：
{{
  "destination": "string",
  "start_date": "string",
  "end_date": "string",
  "preferences": {{
    "activities": ["string"],
    "budget": "string"
  }}
}}

如果用户没有表达旅行意图，请返回所有字段为空。
'''

    def create_default_output() -> dict:
        return {
            "destination": "",
            "start_date": "",
            "end_date": "",
            "preferences": {"activities": [], "budget": ""},
        }

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=None,  # 直接返回字典更灵活
        agent_name="intent_parser",
        default_factory=create_default_output,
    )


def map_budget_to_level(budget_str: str) -> Optional[str]:
    """将预算字符串映射到预算级别"""
    budget_lower = budget_str.lower()
    if any(term in budget_lower for term in ["低", "便宜", "经济", "省", "low"]):
        return "low"
    elif any(term in budget_lower for term in ["高", "豪华", "奢侈", "high"]):
        return "high"
    elif any(term in budget_lower for term in ["中", "适中", "标准", "medium"]):
        return "medium"
    return None


def get_missing_fields(req: ItineraryRequest) -> List[str]:
    """
    检查缺失的必要字段
    
    Args:
        req: 旅行请求对象
        
    Returns:
        缺失字段列表
    """
    # 根据文档要求：满足 destination + dates 即可视为可确认
    missing = []
    if not req.destination:
        missing.append("destination")
    if not req.start_date or not req.end_date:
        missing.append("dates")
    return missing


def generate_followup_question(missing: List[str]) -> str:
    """
    生成后续问题以获取缺失信息
    
    Args:
        missing: 缺失字段列表
        
    Returns:
        后续问题文本
    """
    field_prompts = {
        "destination": "你想去哪？有没有特别想去的城市或景点？",
        "dates": "你打算什么时候出发？准备玩几天？",
        "preferences": "你有什么旅行偏好？比如美食、自然风光、预算等。"
    }
    question = "为了更好地帮您安排行程，我还需要以下信息：\n"
    for field in missing:
        question += f"- {field_prompts[field]}\n"
    
    question += "\n您可以一次性告诉我所有信息，我会帮您规划最适合的行程。"

    return question.strip()
