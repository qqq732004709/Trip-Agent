# cli_main.py

from dotenv import load_dotenv
from runner import run_itinerary
from utils.model_selector import select_model

from langchain_core.messages import HumanMessage

# 调试用：加载 .env 文件
load_dotenv()

def main():
    # CLI 模式选择模型
    model_name, model_provider = select_model(mode="cli")

    # 获取用户输入（或写死测试用）
    print("\n请输入旅行需求，例如：我想去杭州玩三天，喜欢美食和古镇")
    #user_input = input("旅行需求： ").strip()
    user_input = "旅行需求： 我想去广州玩三天，喜欢美食和广州塔还有长隆动物园"
    if not user_input:
        print("❌ 输入为空，退出")
        return

    # 调用同步流程
    itinerary_markdown = run_itinerary(
        input_text=user_input,
        model_name=model_name,
        model_provider=model_provider
    )

    # 输出行程 Markdown
    print("\n🧳 生成的旅行行程 Markdown：\n")
    print(itinerary_markdown)


if __name__ == "__main__":
    main()
