from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List
import json
from utils.llm import LLMClient

class TripAgent:
    def __init__(self):
        # Initialize prompt template
        self.prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""
            你是一个专业的旅行规划助手，请根据以下需求规划旅行行程：
            {user_input}

            请按照以下JSON格式返回：
            {{
                "destination": "目的地名称",
                "days": 天数,
                "plan": [
                    {{
                        "day": 1,
                        "title": "每日主题",
                        "activities": ["活动1", "活动2", ...]
                    }},
                    ...
                ]
            }}
            """
        )
        
        # Initialize LLM client and chain
        self.llm_client = LLMClient()
        self.llm_chain = LLMChain(
            llm=self.llm_client.model,
            prompt=self.prompt
        )

    def generate_itinerary(self, user_input: str) -> Dict:
        """Generate travel itinerary based on user input"""
        try:
            # Get raw LLM response
            response = self.llm_chain.run(user_input=user_input)
            
            # Parse JSON response
            itinerary = json.loads(response.strip())
            
            # Validate structure
            if not all(key in itinerary for key in ["destination", "days", "plan"]):
                raise ValueError("Invalid itinerary format")
                
            return itinerary
            
        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM response as JSON")
        except Exception as e:
            raise ValueError(f"Error generating itinerary: {str(e)}")
