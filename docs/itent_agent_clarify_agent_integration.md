# IntentAgent 和 ClarifyAgent 联动集成文档

## 📚 总体目标

实现一个合理的意图分析流：

1. 首先由 IntentAgent 尽可能地理解用户意图，输出一个最大化补全的 `ItineraryRequest`
2. 把输出通过 `from_request_to_data()` 转成 `ItineraryData`，写入 LangGraph 状态 state\["data"]
3. 进入 ClarifyAgent ，检查还有哪些字段缺失，生成补充问题，归回流程

---

## ✅ 流程规则

### IntentAgent

* 接收用户的输入 messages
* 分析意图，输出 `ItineraryRequest`
* 通过 `from_request_to_data()` 转成并写入 state\["data"]
* 同时设置 metadata\["needs\_clarification"] = True，否则跳过 ClarifyAgent

### ClarifyAgent

* 仅在 metadata\["needs\_clarification"] == True 时进入
* 通过 `from_data_to_request()` 转成 BaseModel
* 按照先后顺序检查哪个字段缺
* 输出补充问题 HumanMessage
* 当字段补全后，设置 metadata\["needs\_clarification"] = False，流程前进

---

## 🔄 LangGraph 联动配置 (pseudo-code)

```python
# 节点配置
nodes = {
    "intent": intent_agent,
    "clarify": clarify_agent,
    "plan": planner_agent,
}

# 条件跳转
edges = {
    "intent": lambda state: "clarify" if state["metadata"].get("needs_clarification") else "plan",
    "clarify": "intent",  # 每补充一次返回 intent 重新理解
}
```

---

## 🔍 优化提示

* IntentAgent 的意图输出该有最小的意图准确级别，不要高估用户意图
* ClarifyAgent 应保持一次补充一个字段，避免输出 prompt 过长
* LangGraph 可设置最大 Clarify 轮数限制（如 3次），超出则提示用户 "信息还不够充分"

---

## 🚀 其他扩展思路

* 后期可以增加 UserProfileAgent，从历史或用户编程情况提前补充 ItineraryData
* 也可将 ClarifyAgent 改为轮询式 multi-turn 话对
