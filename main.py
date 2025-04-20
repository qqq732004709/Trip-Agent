# Load environment variables from .env file
import argparse
from colorama import init
from dotenv import load_dotenv


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