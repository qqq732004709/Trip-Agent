# 🎯 `parse_user_input()` Prompt Engineering 设计文档

## ✨ 功能目标

该 prompt 由 `intent_agent` 调用，用于一次性完成两件事：

1. ✅ 判断用户是否表达了旅行意图；
2. ✅ 若有旅行意图，提取结构化的旅行需求：

   * destination
   * start\_date / end\_date
   * preferences（activities / budget）

---

## 📥 Prompt 输入结构

你传入的上下文是完整对话（多个 HumanMessage 拼接）：

```text
对话记录：
"""
{conversation}
"""
```

---

## 📤 Prompt 目标输出格式

```json
{
  "destination": "string",
  "start_date": "string",
  "end_date": "string",
  "preferences": {
    "activities": ["string"],
    "budget": "string"
  }
}
```

### ❗ 如果没有旅行意图 → 输出所有字段为空

---

## ✅ 当前 Prompt 模板

```text
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
{
  "destination": "string",
  "start_date": "string",
  "end_date": "string",
  "preferences": {
    "activities": ["string"],
    "budget": "string"
  }
}

如果用户没有表达旅行意图，请返回所有字段为空。
```

---

## ✅ Prompt 优势

* 🔁 单次 LLM 调用完成判断 + 提取，减少调用次数
* 💬 具备上下文理解能力（通过完整 conversation）
* 🔐 可安全回退（空结构 = 无意图）

---

## 🧠 建议后续微调方向

| 目标         | 方法                                                |
| ---------- | ------------------------------------------------- |
| 提升结构输出成功率  | 加入“不要解释”、“不要加注释”强调                                |
| 控制预算/偏好多样性 | 加入 examples 提示偏好选项                                |
| 多轮合并       | 后续加入对 memory 的补充示例                                |
| 高可靠性结构化    | 用 LangChain OutputParsers/Function Call 替代简单 JSON |
