from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List
from utils.llm import LLMClient
import json

class HotelAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["destination", "check_in", "check_out", "preferences"],
            template="""
            As a hotel booking expert, recommend hotels in {destination} for dates {check_in} to {check_out}
            matching these preferences: {preferences}.
            
            Return JSON format:
            {
                "destination": "city name",
                "check_in": "date",
                "check_out": "date",
                "hotels": [
                    {
                        "name": "hotel name",
                        "price_range": "$/$$/$$$",
                        "rating": "1-5 stars",
                        "location": "area/district",
                        "amenities": ["list", "of", "amenities"],
                        "booking_link": "example.com"
                    },
                    ...
                ]
            }
            """
        )
        self.llm_client = LLMClient()
        self.chain = LLMChain(llm=self.llm_client.model, prompt=self.prompt)

    def search_hotels(self, destination: str, check_in: str, check_out: str, preferences: Dict) -> Dict:
        """Search hotels based on criteria"""
        try:
            pref_str = ", ".join(f"{k}:{v}" for k,v in preferences.items())
            response = self.chain.run(
                destination=destination,
                check_in=check_in,
                check_out=check_out,
                preferences=pref_str
            )
            return json.loads(response.strip())
        except Exception as e:
            raise ValueError(f"Hotel search failed: {str(e)}")
