# ClarifyAgent 实现提示文档

## 🌟 功能目标

ClarifyAgent 是用于补全用户旅游意图的智能体节点，它在 `ItineraryRequest` 未补全所有字段时：

1. 检查当前 LangGraph 状态 `state["data"]`，根据 `ItineraryData` 定义，找出缺失字段
2. 根据当前状态 `state["messages"]`，生成自然语言 Clarification 问题
3. 返回一条 HumanMessage，进入 LangGraph 完整流程

---

## 📃 状态结构 (`graph/state.py`)

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    data: Annotated[ItineraryData, merge_dicts]
    metadata: Annotated[dict[str, Any], merge_dicts]
```

---

## 📊 模型基础结构

```python
class ItineraryData(TypedDict, total=False):
    destination: str
    start_date: str
    end_date: str
    activity_preferences: List[str]
    pace: Literal["relaxed", "balanced", "intense"]
    scenery_preference: Optional[str]
    budget_level: Literal["low", "medium", "high"]
    max_budget: Optional[float]
    companion_type: Literal["solo", "couple", "family", "friends", "business"]
    companion_notes: Optional[str]
    special_requests: List[str]

class ItineraryRequest(BaseModel):
    ... 同步字段，用于 LLM 输出校验

# 转换方法
from_request_to_data(request: ItineraryRequest) -> ItineraryData
from_data_to_request(data: ItineraryData) -> ItineraryRequest
```

---

## ✅ 输入 / 输出要求

* 输入: 当前状态 `AgentState`
* 输出: 包含 1 条 `HumanMessage` 问题，同时 metadata 标记：

  * `needs_clarification = True/False`
  * `clarify_field = "xxx"`

---

## ⚠️ 开发要点

* 不要一次问多个字段
* 优先问题：destination > date > preferences > budget > companion
* 问题形式为自然语言："您想什么时候出发？"
* 如果没有缺字段，返回 needs\_clarification = False

---

## 🔧 示例逻辑编排 (Copilot 可依此完成)

```python
req = from_data_to_request(state["data"])
missing_fields = find_first_missing(req)

if not missing_fields:
    return {"metadata": {"needs_clarification": False}}

clarify_prompt = build_prompt(missing_fields[0])
response = llm.invoke([... + HumanMessage(content=clarify_prompt)])

return {
    "messages": [response],
    "metadata": {
        "needs_clarification": True,
        "clarify_field": missing_fields[0]
    }
}
```

---

## 📆 文件生成

Copilot 应该生成:

* 文件: `agents/clarify_agent/clarify_agent.py`
* 函数: `async def clarify_agent(state: AgentState) -> Dict:`
* 符合 LangGraph node 输出格式
