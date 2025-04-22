from pydantic import BaseModel
from typing import List, Dict
from graph.state import AgentState
from utils.llm import call_llm
from utils.progress import progress
import json

class ItineraryPlan(BaseModel):
    day: int
    activities: List[str]
    location: str
    notes: str
    details: Dict[str, str]

class ItineraryPlans(BaseModel):
    plans: List[ItineraryPlan]

def itinerary_agent(state: AgentState):
    """Creates a travel itinerary based on user preferences."""
    travel_details = state.get('data').get('travel_details')
    destination = travel_details.get("destination")
    start_date = travel_details.get("start_date")
    end_date = travel_details.get("end_date")
    preferences = travel_details.get("preferences", {})

    progress.update_status("itinerary_agent", status="Validating request")
    validation = validate_travel_request(travel_details)
    if not validation["valid"]:
        return {"error": validation["reason"]}

    progress.update_status("itinerary_agent",status="Generating itinerary")
    itinerary_output = generate_itinerary_output(
        user_request=state,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        preferences=preferences,
        model_name=state["metadata"]["model_name"],
        model_provider=state["metadata"]["model_provider"],
    )

    return itinerary_output

def validate_travel_request(request: Dict) -> Dict:
    """Validate the travel request parameters."""
    if not request.get("destination"):
        return {"valid": False, "reason": "Destination is required"}
    if not request.get("start_date"):
        return {"valid": False, "reason": "Start date is required"}
    if not request.get("end_date"):
        return {"valid": False, "reason": "End date is required"}
    return {"valid": True}

def generate_itinerary_output(
    user_request: Dict,
    destination: str,
    start_date: str,
    end_date: str,
    preferences: Dict,
    model_name: str,
    model_provider: str,
) -> ItineraryPlans:
    """Generate final itinerary output with recommendations."""
    prompt = f"""
Create a detailed travel itinerary for:
Destination: {destination}
Dates: {start_date} to {end_date}
Preferences: {json.dumps(preferences, indent=2)}

Return in this exact JSON format:
{{
  "plans": [
      {{
          "day": int,
          "activities": ["string"],
          "location": "string",
          "notes": "string",
          "details": {{
              "morning": "string",
              "afternoon": "string",
              "evening": "string",
              "transport": "string",
              "dining": "string",
              "cost": "string",
              "weather": "string"
          }}
      }}
  ]
}}
"""


    def create_default_output():
        return []

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=ItineraryPlans,
        agent_name="itinerary_agent",
        default_factory=create_default_output,
    )
