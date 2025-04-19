from typing import Any, Optional
from llm.model import LLMModel

class LLMClient:
    """Core LLM client for making requests"""
    
    def __init__(self, model: Optional[LLMModel] = None):
        self.model = model or LLMModel()
        
    def call_llm(self, prompt: str, **kwargs) -> str:
        """Make a request to the LLM"""
        try:
            if not self.model.configured:
                self.model.configure()
                
            response = self.model.generate(prompt, **kwargs)
            return response
            
        except Exception as e:
            raise RuntimeError(f"LLM request failed: {str(e)}")
            
    def format_response(self, response: str) -> str:
        """Clean and format LLM response"""
        return response.strip()
