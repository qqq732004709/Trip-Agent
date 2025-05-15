from langgraph.graph import MessagesState


# Define agent state
class AgentState(MessagesState):

    # Runtime Variables
    locale: str = "en-US"
    observations: list[str] = []
    plan_iterations: int = 0
    current_plan: str = None
    final_report: str = ""
    auto_accepted_plan: bool = False
    enable_background_investigation: bool = True
    background_investigation_results: str = None
