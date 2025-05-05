from pydantic import BaseModel
from typing import List, Dict
from graph.state import AgentState
from utils.llm import call_llm
from utils.progress import progress
from langchain_core.messages import HumanMessage
import json

class ItineraryRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    preferences: Dict[str, List[str] | str]

def intent_agent(state: AgentState):
    progress.update_status("intent_agent", status="Start processing user input")

    user_input = state["messages"][-1].content

    progress.update_status("intent_agent", status="Parsing user input")
    itinerary_output = parse_user_input(
        user_input,
        model_name=state["metadata"]["model_name"],
        model_provider=state["metadata"]["model_provider"],
    )

    state["data"]["travel_details"] = itinerary_output.dict()

    # Wrap results in a single message
    message = HumanMessage(content=json.dumps(itinerary_output.dict()), name="intent_agent")

    progress.update_status("intent_agent", status="Processing complete")

    return {"messages": [message], "data": state["data"]}

def parse_user_input(
    user_input: str,
    model_name: str,
    model_provider: str,
) -> ItineraryRequest:
    """Parse user input into structured details."""
    prompt = f"""
You are an intelligent assistant. Your task is to parse the following user input into a structured format.

User Input: "{user_input}"

Extract the following details:
- Destination
- Start Date
- End Date
- Preferences (e.g., activities, budget)

Return the extracted details in this exact JSON format:
{{
  "destination": "string",
  "start_date": "string",
  "end_date": "string",
  "preferences": {{
    "activities": ["string"],
    "budget": "string"
  }}
}}
Ensure the output is valid JSON and adheres to the format above.
"""

    def create_default_output():
        return []

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=ItineraryRequest,
        agent_name="intent_parser",
        default_factory=create_default_output,
    )
