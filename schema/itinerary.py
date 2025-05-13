from typing import TypedDict, Optional, Literal, List, Annotated
from pydantic import BaseModel, Field

# === 用于 LangGraph 状态数据的 TypedDict（流转状态） ===

class ItineraryData(TypedDict, total=False):
    destination: str
    start_date: str
    end_date: str

    activity_preferences: List[str]  # ["hot spring", "hiking"]
    pace: Literal["relaxed", "balanced", "intense"]
    scenery_preference: Optional[str]

    budget_level: Literal["low", "medium", "high"]
    max_budget: Optional[float]

    companion_type: Literal["solo", "couple", "family", "friends", "business"]
    companion_notes: Optional[str]

    special_requests: List[str]


# === 用于意图智能体输出的 BaseModel（结构化 JSON 校验） ===

class ItineraryRequest(BaseModel):
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    activity_preferences: List[str] = Field(default_factory=list)
    pace: Optional[Literal["relaxed", "balanced", "intense"]] = None
    scenery_preference: Optional[str] = None

    budget_level: Optional[Literal["low", "medium", "high"]] = None
    max_budget: Optional[float] = None

    companion_type: Optional[Literal["solo", "couple", "family", "friends", "business"]] = None
    companion_notes: Optional[str] = None

    special_requests: List[str] = Field(default_factory=list)


# === 转换函数（方便在 agent 之间转换状态） ===

def from_request_to_data(request: ItineraryRequest) -> ItineraryData:
    return request.model_dump(exclude_none=True, exclude_unset=True)

def from_data_to_request(data: ItineraryData) -> ItineraryRequest:
    return ItineraryRequest.model_validate(data)
