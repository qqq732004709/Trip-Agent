# 📄 intent\_agent 开发说明文档（给 Cursor / 协作者）

## 📌 目标

`intent_agent` 是旅行助手对话流程中的核心 Agent，职责是：

* 🧠 判断用户是否表达了旅行意图；
* 🧾 若有旅行意图，则提取结构化旅行需求（destination, dates, preferences）；
* ❓ 若信息不全，引导用户补充；
* ✅ 若信息充足，标记为 `confirmed = True` 并进入下一阶段；

---

## ✅ 输入

```python
state: AgentState = {
  "messages": List[BaseMessage],  # 包含完整对话历史
  "data": Dict,                   # 存储 travel_details
  "metadata": Dict[str, str]      # 包含 model_name / model_provider
}
```

---

## ✅ 输出

* 修改：

  ```python
  state["data"]["travel_details"] = ItineraryRequest.dict()
  ```
* 返回一条 AIMessage 内容：

  * 信息足够 → 回复“已获取全部需求…”
  * 信息不全 → 回复补充问题列表
  * 无意图 → 回复默认说明并终止

---

## 🧠 逻辑流程

1. 汇总对话历史为 `conversation` 文本；
2. 调用 `parse_user_input(conversation)`，LLM 一次性完成：

   * 意图判断
   * 信息提取
3. 如果结果字段都为空 → 无旅行意图；
4. 如果字段不完整 → 发出补充问题；
5. 字段齐全 → `confirmed = True`，进入下一阶段

---

## 📦 数据结构

```python
class ItineraryRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    preferences: Dict[str, List[str] | str]
    confirmed: bool
```

字段说明：

* `confirmed` 由系统判断设置，不由 LLM 生成
* 满足 destination + preferences 即可视为可确认

---

## 🔐 严格约束（Cursor 严格遵守）

* ❌ 不要调用多个 LLM（所有意图判断 + 信息提取由一个 prompt 完成）
* ❌ 不要让 LLM 返回 confirmed 字段，必须由代码逻辑判断
* ✅ 如果提取失败，使用默认空结构 fallback
* ✅ 如果内容模糊但可能存在旅行意图，允许引导继续提问

---

## 🛠 调试建议

```python
print("🧠 LLM extract:", extracted.dict())
print("🧭 confirmed:", extracted.confirmed)
```

---

## 📍后续扩展建议

* 支持识别“放弃旅行”类意图（如“我不去了”）
* 支持合并补充输入（多轮填空）
* 支持选择推荐方案 vs 自定义
