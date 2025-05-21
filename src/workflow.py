import logging
from src.graph.builder import build_graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

def enble_debug_logging():
    logging.getLogger("src").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

graph = build_graph()


async def run_workflow_async(
        user_input: str,
        max_plan_iterations: int = 5
):
    if not user_input:
        raise ValueError("User input cannot be None")
    
    enble_debug_logging()

    logger.info(f"Starting async workflow with user input: {user_input}")
    initial_state = {
        "messages": [{"role": "user", "content": user_input}],
    }

    config = {
        "configurable": {
            "thread_id":"default",
            "max_plan_iterations": max_plan_iterations
        }
    }

    last_message_cnt = 0
    async for s in graph.astream(
        input=initial_state, config=config, stream_mode="values"
    ):
        try:
            if isinstance(s, dict) and "messages" in s:
                if len(s["messages"]) <= last_message_cnt:
                    continue
                last_message_cnt = len(s["messages"])
                message = s["messages"][-1]
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()
            else:
                # For any other output format
                print(f"Output: {s}")
        except Exception as e:
            logger.error(f"Error processing stream output: {e}")
            print(f"Error processing output: {str(e)}")

    logger.info("Async workflow completed successfully")
