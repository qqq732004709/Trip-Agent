# Load environment variables from .env file
import argparse
import sys
from colorama import Fore, Style, init
from dotenv import load_dotenv
import questionary
from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage
from graph.state import AgentState
from llm.models import LLM_ORDER, OLLAMA_LLM_ORDER, ModelProvider, get_model_info
from utils.progress import progress
from utils.ollama import ensure_ollama_and_model
from agent.itinerary_agent import itinerary_agent

def start(state: AgentState):
    """Initialize the workflow with the input message."""
    return state

def create_workflow():
    """Create the workflow with selected analysts."""
    workflow = StateGraph(AgentState)
    workflow.add_node("start_node", start)

    # Connect start_node to itinerary_agent
    workflow.add_node("itinerary_agent", itinerary_agent)
    workflow.add_edge("start_node", "itinerary_agent")
    workflow.add_edge("itinerary_agent", END)

    workflow.set_entry_point("start_node")
    return workflow

def run_itinerary(model_name: str, model_provider: str):
    """Run the itinerary workflow."""
    try:
        # Start progress tracking
        progress.start()
        progress.update_status("itinerary_agent", status="Initializing")

        # Create the workflow
        workflow = create_workflow()
        agent = workflow.compile()
        progress.update_status("itinerary_agent", status="Workflow created")

        # Prepare user input for the itinerary agent
        user_input = {
            "destination": "Qingdao",
            "start_date": "2025-05-01",
            "end_date": "2025-05-03",
            "preferences": {
                "activities": ["seafood", "sunrise watching", "beer"],
                "budget": "medium"
            }
        }

        # Update progress status
        progress.update_status("itinerary_agent", status="Processing request")

        # Invoke the workflow
        final_state = agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content="Plan an itinerary based on the provided travel details.",
                    )
                ],
                "data": {
                    "travel_details": user_input,
                },
                "metadata": {
                    "model_name": model_name,
                    "model_provider": model_provider,
                },
            },
        )

        progress.update_status("itinerary_agent", status="Done")
        return {
            "itinerary": final_state["messages"][-1].content,
        }
    except Exception as e:
        progress.update_status("itinerary_agent", status=f"Error: {str(e)}")
        raise

load_dotenv()

init(autoreset=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Trip Agent system")
    parser.add_argument("--show-reasoning", action="store_true", help="Show reasoning from each agent")
    parser.add_argument(
        "--show-agent-graph", action="store_true", help="Show the agent graph"
    )
    parser.add_argument(
        "--ollama", action="store_true", help="Use Ollama for local LLM inference"
    )

    args = parser.parse_args()

    # Select LLM model based on whether Ollama is being used
    model_choice = None
    model_provider = None

    if args.ollama:
        print(f"{Fore.CYAN}Using Ollama for local LLM inference.{Style.RESET_ALL}")
        model_choice = questionary.select(
            "Select your Ollama model:",
            choices=[questionary.Choice(display, value=value) for display, value, _ in OLLAMA_LLM_ORDER],
            style=questionary.Style([
                ("selected", "fg:green bold"),
                ("pointer", "fg:green bold"),
                ("highlighted", "fg:green"),
                ("answer", "fg:green bold"),
            ])
        ).ask()

        if not model_choice:
            print("\n\nInterrupt received. Exiting...")
            sys.exit(0)

        if not ensure_ollama_and_model(model_choice):
            print(f"{Fore.RED}Cannot proceed without Ollama and the selected model.{Style.RESET_ALL}")
            sys.exit(1)

        model_provider = ModelProvider.OLLAMA.value
        print(f"\nSelected {Fore.CYAN}Ollama{Style.RESET_ALL} model: {Fore.GREEN + Style.BRIGHT}{model_choice}{Style.RESET_ALL}\n")
    else:
        model_choice = questionary.select(
            "Select your LLM model:",
            choices=[questionary.Choice(display, value=value) for display, value, _ in LLM_ORDER],
            style=questionary.Style([
                ("selected", "fg:green bold"),
                ("pointer", "fg:green bold"),
                ("highlighted", "fg:green"),
                ("answer", "fg:green bold"),
            ])
        ).ask()

        if not model_choice:
            print("\n\nInterrupt received. Exiting...")
            sys.exit(0)
        else:
            model_info = get_model_info(model_choice)
            if model_info:
                model_provider = model_info.provider.value
                print(f"\nSelected {Fore.CYAN}{model_provider}{Style.RESET_ALL} model: {Fore.GREEN + Style.BRIGHT}{model_choice}{Style.RESET_ALL}\n")
            else:
                model_provider = "Unknown"
                print(f"\nSelected model: {Fore.GREEN + Style.BRIGHT}{model_choice}{Style.RESET_ALL}\n")

    # Run the itinerary workflow
    result = run_itinerary(model_name=model_choice, model_provider=model_provider)
    print(f"\nGenerated Itinerary:\n{Fore.GREEN}{result['itinerary']}{Style.RESET_ALL}")