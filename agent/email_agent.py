from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List
from utils.llm import LLMClient
import json

class EmailAgent:
    def __init__(self):
        self.summary_prompt = PromptTemplate(
            input_variables=["email_content"],
            template="""
            Analyze this travel-related email and extract key information:
            {email_content}
            
            Return JSON format:
            {
                "sender": "email sender",
                "summary": "brief summary",
                "travel_details": {
                    "destinations": ["list", "of", "places"],
                    "dates": ["start_date", "end_date"],
                    "people": ["list", "of", "names"]
                },
                "action_items": ["list", "of", "actions"],
                "priority": "high/medium/low"
            }
            """
        )
        self.llm_client = LLMClient()
        self.summary_chain = LLMChain(llm=self.llm_client.model, prompt=self.summary_prompt)

    def process_email(self, email_content: str) -> Dict:
        """Extract travel info from email"""
        try:
            response = self.summary_chain.run(email_content=email_content)
            return json.loads(response.strip())
        except Exception as e:
            raise ValueError(f"Email processing failed: {str(e)}")

    def generate_response(self, email_data: Dict) -> str:
        """Generate draft response to travel email"""
        # Could be extended with more sophisticated response generation
        return f"""Re: Your travel plans\n\nSummary: {email_data['summary']}\n\nNext steps:\n- """ + "\n- ".join(email_data['action_items'])
