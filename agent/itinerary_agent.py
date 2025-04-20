from pydantic import BaseModel
from typing import List, Dict, Literal
from graph import state
from utils.llm import call_llm
from utils.progress import progress
import json

class ItineraryPlan(BaseModel):
    day: int
    activities: List[str]
    location: str
    notes: str

class ItinerarySignal(BaseModel):
    status: Literal["recommended", "not_recommended", "neutral"]
    confidence: float
    reasoning: str

def itinerary_agent(user_request: Dict):
    """Creates a travel itinerary based on user preferences."""
    destination = user_request.get("destination")
    start_date = user_request.get("start_date")
    end_date = user_request.get("end_date")
    preferences = user_request.get("preferences", {})

    progress.update_status("itinerary_agent", "Validating request")
    validation = validate_travel_request(user_request)
    if not validation["valid"]:
        return {"error": validation["reason"]}

    progress.update_status("itinerary_agent", "Analyzing destination")
    destination_analysis = analyze_destination(destination, preferences)

    progress.update_status("itinerary_agent", "Generating itinerary")
    itinerary = generate_base_itinerary(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        preferences=preferences,
        destination_analysis=destination_analysis
    )

    progress.update_status("itinerary_agent", "Validating itinerary")
    validation = validate_itinerary(itinerary)
    if not validation["valid"]:
        return {"error": validation["reason"]}

    progress.update_status("itinerary_agent", "Optimizing itinerary")
    optimized_itinerary = optimize_itinerary(
        itinerary=itinerary,
        preferences=preferences
    )

    progress.update_status("itinerary_agent", "Generating final output")
    itinerary_output = generate_itinerary_output(
        user_request=user_request,
        itinerary_data=optimized_itinerary,
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

def analyze_destination(destination: str, preferences: Dict) -> Dict:
    """Analyze destination suitability based on preferences."""
    # This would be expanded with actual destination analysis logic
    return {
        "safety": "high",
        "budget": "medium",
        "attractions": ["cultural", "historical"],
        "accessibility": "good"
    }

def generate_base_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    preferences: Dict,
    destination_analysis: Dict
) -> List[ItineraryPlan]:
    """Generate initial itinerary using LLM."""
    prompt = f"""
    Create a detailed travel itinerary for:
    Destination: {destination}
    Dates: {start_date} to {end_date}
    Preferences: {json.dumps(preferences, indent=2)}
    Destination Analysis: {json.dumps(destination_analysis, indent=2)}

    Return in this exact JSON format:
    [
        {{
            "day": int,
            "activities": ["string"],
            "location": "string",
            "notes": "string"
        }}
    ]
    """

    def create_default_itinerary():
        return []

    return call_llm(
        prompt=prompt,
        model_name="gpt-4",
        model_provider="openai",
        pydantic_model=List[ItineraryPlan],
        agent_name="itinerary_agent",
        default_factory=create_default_itinerary,
    )

def validate_itinerary(itinerary: List[ItineraryPlan]) -> Dict:
    """Validate the generated itinerary."""
    if not itinerary:
        return {"valid": False, "reason": "Empty itinerary generated"}
    if len(itinerary) == 0:
        return {"valid": False, "reason": "No days in itinerary"}
    return {"valid": True}

def optimize_itinerary(itinerary: List[ItineraryPlan], preferences: Dict) -> List[ItineraryPlan]:
    """Optimize itinerary based on preferences."""
    # This would be expanded with actual optimization logic
    return itinerary

def generate_itinerary_output(
    user_request: Dict,
    itinerary_data: List[ItineraryPlan],
    model_name: str,
    model_provider: str,
) -> Dict:
    """Generate final itinerary output with recommendations."""
    from langchain_core.prompts import ChatPromptTemplate

    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert travel planning AI. Create a polished itinerary with:
                1. Daily schedule with time allocations
                2. Transportation details between locations
                3. Restaurant recommendations matching preferences
                4. Cost estimates for activities
                5. Weather considerations
                6. Local tips and cultural notes

                For each day, provide:
                - Morning, afternoon, evening activities
                - Travel time estimates
                - Recommended restaurants with cuisine types
                - Estimated costs
                - Any special considerations

                Also provide overall recommendations about:
                - Best times to visit attractions
                - Money-saving tips
                - Safety considerations
                - Packing suggestions
                """,
            ),
            (
                "human",
                """Create a final travel itinerary based on:

                User Request:
                {user_request}

                Itinerary Data:
                {itinerary_data}

                Return in this exact JSON format:
                {{
                    "itinerary": [
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
                    ],
                    "recommendations": {{
                        "status": "recommended" | "not_recommended" | "neutral",
                        "confidence": float,
                        "reasoning": "string",
                        "tips": [
                            "string"
                        ],
                        "safety": "string",
                        "packing": "string"
                    }}
                }}
                """,
            ),
        ]
    )

    prompt = template.invoke({
        "user_request": json.dumps(user_request, indent=2),
        "itinerary_data": json.dumps([plan.model_dump() for plan in itinerary_data], indent=2)
    })

    def create_default_output():
        return {
            "itinerary": [],
            "recommendations": {
                "status": "neutral",
                "confidence": 0.0,
                "reasoning": "Error generating recommendations",
                "tips": [],
                "safety": "Unknown",
                "packing": "Unknown"
            }
        }

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=Dict,
        agent_name="itinerary_agent",
        default_factory=create_default_output,
    )
