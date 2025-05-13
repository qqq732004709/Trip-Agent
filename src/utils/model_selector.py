from llm.models import LLM_ORDER, get_model_info
import os

def select_model(mode: str = "cli", st=None):
    """
    Select an LLM model via CLI or Streamlit.

    Args:
        mode (str): "cli" or "streamlit"
        st (streamlit module): Required only in Streamlit mode

    Returns:
        Tuple[str, str]: (model_name, provider)
    """
    if mode == "cli":
        import questionary
        from colorama import Fore, Style
        from questionary import Choice, Style as QStyle

        choice = questionary.select(
            "Select your LLM model:",
            choices=[Choice(display, value=value) for display, value, _ in LLM_ORDER],
            style=QStyle([
                ("selected", "fg:green bold"),
                ("pointer", "fg:green bold"),
                ("highlighted", "fg:green"),
                ("answer", "fg:green bold"),
            ])
        ).ask()

        if not choice:
            print("\n\nInterrupt received. Exiting...")
            import sys
            sys.exit(0)

        info = get_model_info(choice)
        provider = info.provider.value if info else "Unknown"

        print(f"\nSelected {Fore.CYAN}{provider}{Style.RESET_ALL} model: {Fore.GREEN + Style.BRIGHT}{choice}{Style.RESET_ALL}\n")
        return choice, provider

    elif mode == "streamlit":
        if st is None:
            raise ValueError("Streamlit module is required for streamlit mode.")

        st.sidebar.header("🧠 模型选择")

        model_display_names = [display for display, _, _ in LLM_ORDER]
        model_display_to_internal = {display: (value, provider) for display, value, provider in LLM_ORDER}

        selected_display = st.sidebar.selectbox("模型列表", model_display_names)
        model_name, provider = model_display_to_internal[selected_display]

        st.sidebar.markdown(f"✅ 当前模型: `{model_name}`（提供商: `{provider}`）")
        return model_name, provider

    else:
        raise ValueError("Invalid mode. Choose 'cli' or 'streamlit'.")
