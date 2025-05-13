import streamlit as st
from dotenv import load_dotenv
from runner import run_itinerary
from src.utils.model_selector import select_model
from src.utils.progress import init_progress

# Load environment variables
load_dotenv()

# Streamlit page setup
st.set_page_config(page_title="旅行助手 Trip-Agent", layout="wide")
st.title("🧳 旅行助手 Trip-Agent")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 选择模型（从 utils 封装中调用）
model_name, model_provider = select_model(mode="streamlit", st=st)

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 主逻辑：处理用户输入
if user_prompt := st.chat_input("请输入旅行需求，例如：我想去成都玩三天，喜欢美食和文化"):

    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 响应占位符
    with st.chat_message("assistant"):
        placeholder = st.empty()
        init_progress(mode="streamlit", st_ref=st, ui_placeholder=placeholder)

        try:
            # 同步调用 runner.py 中封装的流程
            itinerary_markdown = run_itinerary(
                input_text=user_prompt,
                model_name=model_name,
                model_provider=model_provider
            )

            placeholder.markdown(itinerary_markdown)
            st.session_state.messages.append({"role": "assistant", "content": itinerary_markdown})

        except Exception as e:
            error_msg = f"❌ 出错了：{e}"
            placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
