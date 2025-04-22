from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List
from utils.llm import LLMClient

class LocationAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["destination", "interests"],
            template="""
            As a travel location expert, recommend specific places in {destination} 
            matching these interests: {interests}.
            
            Return JSON format:
            {
                "destination": "city name",
                "recommendations": [
                    {
                        "name": "place name",
                        "type": "attraction/restaurant/etc",
                        "description": "brief description",
                        "why_recommend": "why it matches interests"
                    },
                    ...
                ]
            }
            """
        )
        self.llm_client = LLMClient()
        self.chain = LLMChain(llm=self.llm_client.model, prompt=self.prompt)

    def recommend_locations(self, destination: str, interests: List[str]) -> Dict:
        """Get location recommendations based on destination and interests"""
        try:
            response = self.chain.run(destination=destination, interests=", ".join(interests))
            return json.loads(response.strip())
        except Exception as e:
            raise ValueError(f"Location recommendation failed: {str(e)}")
