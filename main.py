# Load environment variables from .env file
import argparse
import sys
from colorama import Fore, Style, init
from dotenv import load_dotenv
import questionary

from llm.model import LLM_ORDER, OLLAMA_LLM_ORDER, ModelProvider, get_model_info
from utils.ollama import ensure_ollama_and_model


load_dotenv()

init(autoreset=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the skyhotbot system")
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
        
        # Select from Ollama-specific models
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
        
        # Ensure Ollama is installed, running, and the model is available
        if not ensure_ollama_and_model(model_choice):
            print(f"{Fore.RED}Cannot proceed without Ollama and the selected model.{Style.RESET_ALL}")
            sys.exit(1)
        
        model_provider = ModelProvider.OLLAMA.value
        print(f"\nSelected {Fore.CYAN}Ollama{Style.RESET_ALL} model: {Fore.GREEN + Style.BRIGHT}{model_choice}{Style.RESET_ALL}\n")
    else:
        # Use the standard cloud-based LLM selection
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
            # Get model info using the helper function
            model_info = get_model_info(model_choice)
            if model_info:
                model_provider = model_info.provider.value
                print(f"\nSelected {Fore.CYAN}{model_provider}{Style.RESET_ALL} model: {Fore.GREEN + Style.BRIGHT}{model_choice}{Style.RESET_ALL}\n")
            else:
                model_provider = "Unknown"
                print(f"\nSelected model: {Fore.GREEN + Style.BRIGHT}{model_choice}{Style.RESET_ALL}\n")