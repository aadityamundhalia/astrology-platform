import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from config import get_settings
import logging
import json
import re

logger = logging.getLogger(__name__)
settings = get_settings()

class ExtractionAgent:
    def __init__(self):
        self.kernel = sk.Kernel()
        
        # Add Ollama service
        self.service_id = "ollama"
        chat_service = OllamaChatCompletion(
            service_id=self.service_id,
            ai_model_id=settings.ollama_model,
            host=settings.ollama_host
        )
        self.kernel.add_service(chat_service)
        
        self.system_prompt = """You are a data extraction agent. Your only job is to extract birth details from user messages.

Respond ONLY in this exact JSON format:
{
  "date_of_birth": "YYYY-MM-DD or null",
  "time_of_birth": "HH:MM or null",
  "place_of_birth": "City, Region/State or null"
}

Rules:
- If data is not available, use null (not string "null")
- Date must be in YYYY-MM-DD format
- Time must be in HH:MM format (24-hour)
- Place must include city and region/state separated by comma
- Return ONLY valid JSON, nothing else
- No explanations, no extra text

Examples:
Input: "I was born on November 22, 1970 at 12:25 AM in Hisar, Haryana"
Output: {"date_of_birth": "1970-11-22", "time_of_birth": "00:25", "place_of_birth": "Hisar, Haryana"}

Input: "My birthday is 15th March 1985"
Output: {"date_of_birth": "1985-03-15", "time_of_birth": null, "place_of_birth": null}

Input: "How is my day today?"
Output: {"date_of_birth": null, "time_of_birth": null, "place_of_birth": null}"""
    
    async def extract_birth_data(self, message: str) -> dict:
        """Extract birth data from user message"""
        try:
            # Create chat history
            chat_history = ChatHistory()
            chat_history.add_system_message(self.system_prompt)
            chat_history.add_user_message(message)
            
            # Get chat completion service
            chat_service = self.kernel.get_service(self.service_id)
            
            # Create execution settings
            execution_settings = PromptExecutionSettings(
                service_id=self.service_id,
                extension_data={
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "max_tokens": 500
                }
            )
            
            # Get response
            response = await chat_service.get_chat_message_content(
                chat_history=chat_history,
                settings=execution_settings
            )
            
            response_text = str(response).strip()
            logger.info(f"Extraction response: {response_text}")
            
            # Parse JSON response
            try:
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    data = json.loads(response_text)
                
                # Validate and clean data
                result = {
                    "date_of_birth": data.get("date_of_birth") if data.get("date_of_birth") else None,
                    "time_of_birth": data.get("time_of_birth") if data.get("time_of_birth") else None,
                    "place_of_birth": data.get("place_of_birth") if data.get("place_of_birth") else None
                }
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}, Response: {response_text}")
                return {
                    "date_of_birth": None,
                    "time_of_birth": None,
                    "place_of_birth": None
                }
                
        except Exception as e:
            logger.error(f"Error in extract_birth_data: {e}", exc_info=True)
            return {
                "date_of_birth": None,
                "time_of_birth": None,
                "place_of_birth": None
            }
