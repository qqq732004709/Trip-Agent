import pytest
from src.agent.intent_agent import parse_user_input, ItineraryData
from src.llm.models import ModelProvider
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "deepseek-chat"
MODEL_PROVIDER = ModelProvider.DEEPSEEK

@pytest.mark.parametrize("user_input", [
    "我想去青岛玩三天，预算中等，喜欢看海和吃海鲜",
    "5月2日出发去成都，5月5日回来，住市中心就好",
    "帮我安排行程，我喜欢爬山和安静的地方",
    "我要去东京旅游，安排一个 4 天的行程，最好能泡温泉",
    "推荐一个地方，时间不限，喜欢美食",
])
def test_parse_user_input(user_input):
    result: ItineraryData = parse_user_input(
        user_input,
        model_name=MODEL_NAME,
        model_provider=MODEL_PROVIDER
    )

    print("\n🧪 测试输入：", user_input)
    print("📦 输出结构：", result.model_dump_json())

    assert isinstance(result, ItineraryData)
    assert result.destination is not None and isinstance(result.destination, str)
    assert isinstance(result.preferences, dict)
