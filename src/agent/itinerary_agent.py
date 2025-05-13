from pydantic import BaseModel
from typing import List, Dict
from src.graph.state import AgentState
from src.utils.llm import call_llm
from src.utils.progress import progress
from langchain_core.messages import HumanMessage
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
    return state.get("data", {})

# def itinerary_agent(state: AgentState):
#     """Creates a travel itinerary based on user preferences."""
#     progress().update_status("itinerary_agent", status="Start processing travel itinerary")

#     # Access the data directly from state and handle missing fields gracefully
#     itinerary_data = state.get('data', {})
    
#     # Create a dictionary with default values for each field
#     travel_details = {
#         "destination": itinerary_data.get("destination", "Unknown location"),
#         "start_date": itinerary_data.get("start_date", "Not specified"),
#         "end_date": itinerary_data.get("end_date", "Not specified"),
#         "activity_preferences": itinerary_data.get("activity_preferences", []),
#         "budget_level": itinerary_data.get("budget_level", "medium"),
#         "scenery_preference": itinerary_data.get("scenery_preference", "")
#     }

#     progress().update_status("itinerary_agent", status="Validating travel request")
#     validation = validate_travel_request(travel_details)
#     if not validation["valid"]:
#         return {"error": validation["reason"]}

#     # Build preferences dict for the generator from available data
#     preferences = {
#         "activities": travel_details["activity_preferences"],
#         "budget": travel_details["budget_level"],
#         "scenery": travel_details["scenery_preference"]
#     }

#     progress().update_status("itinerary_agent", status="Generating travel itinerary")
#     itinerary_output = generate_itinerary_output(
#         destination=travel_details["destination"],
#         start_date=travel_details["start_date"],
#         end_date=travel_details["end_date"],
#         preferences=preferences,
#         model_name=state["metadata"]["model_name"],
#         model_provider=state["metadata"]["model_provider"],
#     )

#     progress().update_status("itinerary_agent", status="Converting itinerary to markdown")
#     # Convert itinerary to markdown format
#     itinerary_markdown = convert_plans_to_markdown(itinerary_output)

#     # Add markdown to data
#     state["data"]["itinerary_markdown"] = itinerary_markdown

#     progress().update_status("itinerary_agent", status="done")
#     # Wrap results in a single message
#     message = HumanMessage(content=f"已为您生成{travel_details['destination']}的行程安排。")

#     return {"messages": [message], "data": state["data"]}

def validate_travel_request(request: Dict) -> Dict:
    """Validate the travel request parameters."""
    if not request.get("destination") or request["destination"] == "Unknown location":
        return {"valid": False, "reason": "Destination is required"}
    return {"valid": True}

def generate_itinerary_output(
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
        return ItineraryPlans(plans=[
            ItineraryPlan(
                day=1,
                activities=["City exploration"],
                location=destination,
                notes="Basic sightseeing tour",
                details={
                    "morning": "Visit main attractions",
                    "afternoon": "Local cuisine experience",
                    "evening": "Rest at accommodation",
                    "transport": "Public transportation",
                    "dining": "Local restaurants",
                    "cost": "Medium",
                    "weather": "Check local forecast"
                }
            )
        ])

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=ItineraryPlans,
        agent_name="itinerary_agent",
        default_factory=create_default_output,
    )

def convert_plans_to_markdown(plans: ItineraryPlans) -> str:
    """Convert itinerary plans to markdown format."""
    markdown = "# Travel Itinerary\n\n"
    for plan in plans.plans:
        markdown += f"## Day {plan.day}: {plan.location}\n"
        markdown += f"**Activities:** {', '.join(plan.activities)}\n\n"
        markdown += f"**Notes:** {plan.notes}\n\n"
        markdown += "### Details:\n"
        for key, value in plan.details.items():
            markdown += f"- **{key.capitalize()}:** {value}\n"
        markdown += "\n"
    return markdown
