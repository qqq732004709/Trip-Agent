from langchain_core.messages import AIMessage, HumanMessage
from utils.llm import get_llm, call_llm
from pydantic import BaseModel
from typing import List, Dict, Union
import json
from utils.progress import progress
from graph.state import AgentState

class ItineraryRequest(BaseModel):
    destination: str = ""
    start_date: str = ""
    end_date: str = ""
    preferences: Dict[str, Union[List[str], str]] = {}
    confirmed: bool = False

def intent_agent(state: AgentState):
    progress().update_status("intent_agent", "⏳ 尝试理解用户需求")

    user_input = state["messages"][-1].content
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]

    full_conversation = "\n".join([
        m.content for m in state["messages"] if isinstance(m, HumanMessage)
    ])

    # 一次性解析意图 + 结构
    extracted = parse_user_input(full_conversation, model_name, model_provider)

    # 如果提取结果为空，说明没有旅行意图
    if not extracted.destination and not extracted.preferences:
        progress().update_status("intent_agent", "⚠️ 似乎不是旅行相关意图，终止流程")
        return {
            "data": state["data"],
            "messages": [
                AIMessage(content="目前我专注于旅行相关的任务，例如安排行程、推荐景点等。如果您需要帮助，请告诉我有关您的旅行计划～")
            ]
        }

    missing_fields = get_missing_fields(extracted)

    if not missing_fields:
        extracted.confirmed = True
        progress().update_status("intent_agent", "✅ 已获取完整需求")
        return {
            "data": {"travel_details": extracted.dict()},
            "messages": [
                AIMessage(content="太好了，我已经获取了您的全部旅行需求，即将为您规划行程。")
            ]
        }
    else:
        progress().update_status("intent_agent", "❓ 需求不完整，等待用户补充")
        llm = get_llm(model_name, model_provider)
        followup = generate_followup_question(missing_fields, llm)
        return {
            "data": {"travel_details": extracted.dict()},
            "messages": [AIMessage(content=followup)]
        }

def parse_user_input(conversation: str, model_name: str, model_provider: str) -> ItineraryRequest:
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
请严格输出 JSON 格式，结构如下：
{{
  "destination": "string",
  "start_date": "string",
  "end_date": "string",
  "preferences": {{
    "activities": ["string"],
    "budget": "string"
  }}
}}

如果用户没有表达旅行意图，请返回空字段。
'''

    def create_default_output():
        return ItineraryRequest(
            destination="",
            start_date="",
            end_date="",
            preferences={"activities": [], "budget": ""},
        )

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=ItineraryRequest,
        agent_name="intent_parser",
        default_factory=create_default_output,
    )

def get_missing_fields(req: ItineraryRequest) -> List[str]:
    if not req.destination and not req.preferences:
        return ["destination", "preferences"]

    missing = []
    if not req.destination:
        missing.append("destination")
    if not req.start_date or not req.end_date:
        missing.append("dates")
    return missing

def generate_followup_question(missing: List[str], llm) -> str:
    field_prompts = {
        "destination": "你想去哪？有没有特别想去的城市或景点？",
        "dates": "你打算什么时候出发？准备玩几天？",
        "preferences": "你有什么旅行偏好？比如美食、自然风光、预算等。"
    }
    question = "为了更好地帮您安排行程，我还需要以下信息：\n"
    for field in missing:
        question += f"- {field_prompts[field]}\n"

    return question.strip()
