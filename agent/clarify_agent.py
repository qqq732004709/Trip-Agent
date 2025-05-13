from typing import Dict, List, Optional
from langchain_core.messages import AIMessage  # 改为 AIMessage
from graph.state import AgentState
from schema.itinerary import from_data_to_request
from utils.progress import progress

# Field priority order (from highest to lowest)
FIELD_PRIORITY = [
    "destination",
    "start_date", 
    "end_date",
    "activity_preferences",
    "pace",
    "scenery_preference",
    "budget_level",
    "max_budget",
    "companion_type",
    "companion_notes",
    "special_requests"
]

# Templates for questions about each field
FIELD_QUESTIONS = {
    "destination": "您想去哪个目的地旅行？",
    "start_date": "您计划什么时候出发？",
    "end_date": "您计划旅行到什么时候结束？",
    "activity_preferences": "您在旅行中有什么特别喜欢的活动吗？例如徒步、温泉、博物馆参观等。",
    "pace": "您希望旅行的节奏是怎样的？轻松悠闲(relaxed)、均衡(balanced)还是紧凑充实(intense)？",
    "scenery_preference": "您有什么特别喜欢的风景类型吗？比如海滩、山脉、城市景观等。",
    "budget_level": "您的预算水平是低(low)、中(medium)还是高(high)？",
    "max_budget": "您的最大预算是多少？请提供一个具体的金额。",
    "companion_type": "您是独自旅行(solo)、情侣出游(couple)、家庭旅行(family)、朋友出行(friends)还是商务旅行(business)？",
    "companion_notes": "关于您的同行人，有什么需要特别注意的吗？例如老人、儿童或有特殊需求的同伴。",
    "special_requests": "您有什么特别的要求或偏好吗？例如素食餐厅推荐、无障碍设施需求等。"
}

def find_first_missing(req_dict: Dict) -> Optional[str]:
    """
    Find the first missing field according to priority order
    """
    for field in FIELD_PRIORITY:
        # Check if field is missing or empty
        if field not in req_dict or req_dict[field] is None:
            # For list fields, check if they're empty
            if field in req_dict and isinstance(req_dict[field], list) and len(req_dict[field]) == 0:
                return field
            # For other fields, missing or None means we need to clarify
            if field not in req_dict or req_dict[field] is None:
                return field
    return None

def clarify_agent(state: AgentState) -> Dict:
    """
    Agent to check for missing fields and generate questions to complete the itinerary
    
    Args:
        state: Current state of the agent conversation
        
    Returns:
        Dict with messages and metadata
    """
    progress().update_status("clarify_agent", "⏳ 检查需要澄清的信息")
    
    # Only proceed if needs_clarification is True
    if state["metadata"].get("needs_clarification") is False:
        progress().update_status("clarify_agent", "✓ 无需澄清")
        return {
            "metadata": {
                "needs_clarification": False
            }
        }
    
    # Convert current data to request object to check missing fields
    req = from_data_to_request(state["data"])
    req_dict = req.model_dump()
    
    # Find first missing field based on priority
    missing_field = find_first_missing(req_dict)
    
    # If no missing fields, return with needs_clarification = False
    if not missing_field:
        progress().update_status("clarify_agent", "✅ 所有信息已完备")
        return {
            "metadata": {
                "needs_clarification": False
            }
        }
    
    # Get question template for the missing field
    question = FIELD_QUESTIONS[missing_field]
    progress().update_status("clarify_agent", f"❓ 需要澄清: {missing_field}")
    
    # 将返回消息类型从 HumanMessage 改为 AIMessage
    return {
        "messages": [AIMessage(content=question)],
        "metadata": {
            "needs_clarification": True,
            "clarify_field": missing_field
        }
    }