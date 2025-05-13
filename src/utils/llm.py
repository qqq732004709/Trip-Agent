"""Helper functions for LLM"""

import json
from typing import TypeVar, Type, Optional, Any, Dict, Union
from pydantic import BaseModel
from src.utils.progress import progress

T = TypeVar('T', bound=BaseModel)

def call_llm(
    prompt: Any,
    model_name: str,
    model_provider: str,
    pydantic_model: Optional[Type[T]] = None,
    agent_name: Optional[str] = None,
    max_retries: int = 3,
    default_factory = None
) -> Union[T, Dict, Any]:
    """
    Makes an LLM call with retry logic, handling both JSON supported and non-JSON supported models.
    
    Args:
        prompt: The prompt to send to the LLM
        model_name: Name of the model to use
        model_provider: Provider of the model
        pydantic_model: The Pydantic model class to structure the output, or None for raw output
        agent_name: Optional name of the agent for progress updates
        max_retries: Maximum number of retries (default: 3)
        default_factory: Optional factory function to create default response on failure
        
    Returns:
        An instance of the specified Pydantic model, or raw output if pydantic_model is None
    """
    from src.llm.models import get_model, get_model_info
    
    model_info = get_model_info(model_name)
    llm = get_model(model_name, model_provider)
    
    # For non-JSON support models, we can use structured output if a model is provided
    if pydantic_model is not None and not (model_info and not model_info.has_json_mode()):
        llm = llm.with_structured_output(
            pydantic_model,
            method="json_mode",
        )
    
    # Call the LLM with retries
    for attempt in range(max_retries):
        try:
            # Call the LLM
            result = llm.invoke(prompt)
            
            # If pydantic_model is None, return raw result or try to extract JSON
            if pydantic_model is None:
                if hasattr(result, 'content'):
                    content = result.content
                    try:
                        # Try to parse as JSON if it looks like JSON
                        if content.strip().startswith('{') and content.strip().endswith('}'):
                            return json.loads(content)
                        else:
                            parsed = extract_json_from_response(content)
                            if parsed:
                                return parsed
                    except json.JSONDecodeError:
                        pass
                return result
            
            # For non-JSON support models with a pydantic model
            if model_info and not model_info.has_json_mode():
                parsed_result = extract_json_from_response(result.content)
                if parsed_result:
                    return pydantic_model(**parsed_result)
            
            return result
                
        except Exception as e:
            if agent_name:
                progress().update_status(agent_name, f"Error - retry {attempt + 1}/{max_retries}")
            
            if attempt == max_retries - 1:
                print(f"Error in LLM call after {max_retries} attempts: {e}")
                # Use default_factory if provided, otherwise create a basic default
                if default_factory:
                    return default_factory()
                elif pydantic_model is not None:
                    return create_default_response(pydantic_model)
                else:
                    return {} if default_factory is None else default_factory()

    # This should never be reached due to the retry logic above
    if pydantic_model is not None:
        return create_default_response(pydantic_model)
    return {}

def create_default_response(model_class: Type[T]) -> T:
    """Creates a safe default response based on the model's fields."""
    if model_class is None:
        return {}
        
    default_values = {}
    for field_name, field in model_class.model_fields.items():
        if field.annotation == str:
            default_values[field_name] = "Error in analysis, using default"
        elif field.annotation == float:
            default_values[field_name] = 0.0
        elif field.annotation == int:
            default_values[field_name] = 0
        elif hasattr(field.annotation, "__origin__") and field.annotation.__origin__ == dict:
            default_values[field_name] = {}
        else:
            # For other types (like Literal), try to use the first allowed value
            if hasattr(field.annotation, "__args__"):
                default_values[field_name] = field.annotation.__args__[0]
            else:
                default_values[field_name] = None
    
    return model_class(**default_values)

def extract_json_from_response(content: str) -> Optional[dict]:
    """Extracts JSON from markdown-formatted response."""
    try:
        json_start = content.find("```json")
        if json_start != -1:
            json_text = content[json_start + 7:]  # Skip past ```json
            json_end = json_text.find("```")
            if json_end != -1:
                json_text = json_text[:json_end].strip()
                return json.loads(json_text)
        
        # Also check for just plain JSON content without markdown formatting
        if content.strip().startswith('{') and content.strip().endswith('}'):
            return json.loads(content)
    except Exception as e:
        print(f"Error extracting JSON from response: {e}")
    return None
