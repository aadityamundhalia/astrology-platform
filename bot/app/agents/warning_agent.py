"""Warning Agent for generating contextual profanity warnings using Semantic Kernel"""
import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.connectors.ai.ollama.ollama_prompt_execution_settings import OllamaChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class WarningAgent:
    def __init__(self):
        self.kernel = sk.Kernel()
        
        # Add Ollama service (same as your other agents)
        self.service_id = "ollama"
        chat_service = OllamaChatCompletion(
            service_id=self.service_id,
            ai_model_id=settings.ollama_model,
            host=settings.ollama_host
        )
        self.kernel.add_service(chat_service)
        
        self.system_prompt = """You are Rudie 🌿, a friendly but firm astrology bot from Australia.

A user just sent you a rude or offensive message. Your job is to politely but clearly tell them this isn't acceptable.

PERSONALITY:
- Stay in character as Rudie (Australian, cosmic guide, friendly)
- Be firm but not preachy
- Keep it under 150 words
- Use 1-2 emojis naturally (🌿, ⚠️, 🌙, ✨)
- Write in plain paragraphs, no lists or bullet points

TONE BY STRIKE COUNT:
- First strike: Understanding but clear - give them a chance
- Second strike: Firmer - this is serious now
- Third strike: Final warning - emphasize consequences

STRUCTURE:
1. Acknowledge but don't repeat their offensive words
2. Clearly state this language isn't acceptable
3. Remind them to be respectful
4. Either encourage them to rephrase (strike 1-2) or warn about suspension (strike 3+)

EXAMPLES:

FIRST STRIKE:
"Hey mate, I hear you're frustrated, but let's keep it respectful, yeah? 🌿 I'm here to help with your cosmic questions, but I need you to communicate politely. Can you rephrase that and ask again nicely? Cheers! ✨"

SECOND STRIKE:
"Right, I need you to watch your language. ⚠️ I'm happy to help you with the stars, but this is your second warning. Let's keep things respectful from here on out. Can you rephrase that question for me? 🌿"

FINAL WARNING (3+ strikes):
"That's your final warning. ⚠️ I've been patient, but one more incident like this and your account will be suspended. I'm here to guide you through the stars, not to cop abuse. Let's keep it civil, or we're done here. Your choice, mate. 🌿"

Keep it natural, direct, and in character!"""
    
    async def generate_warning(
        self, 
        user_message: str,
        reason: str,
        user_name: str,
        strikes: int
    ) -> str:
        """Generate a contextual warning response"""
        try:
            # Determine severity
            if strikes >= 2:
                severity = "FINAL WARNING (3+ strikes)"
            elif strikes == 1:
                severity = "SECOND WARNING"
            else:
                severity = "FIRST WARNING"
            
            # Build user message for the agent
            prompt = f"""User: {user_name}
Strike Level: {severity}
Why flagged: {reason}
Offensive message: "{user_message}"

Generate your warning response as Rudie. Remember:
- Don't repeat their offensive words
- Be firm but stay in character
- {"EMPHASIZE this is the FINAL warning and suspension is next" if strikes >= 2 else "Give them a chance to rephrase" if strikes == 1 else "Be understanding but clear"}
- Keep it under 150 words
- Use 1-2 emojis naturally"""
            
            # Create chat history
            chat_history = ChatHistory()
            chat_history.add_system_message(self.system_prompt)
            chat_history.add_user_message(prompt)
            
            # Get chat completion service
            chat_service = self.kernel.get_service(self.service_id)
            
            # Create execution settings
            execution_settings = OllamaChatPromptExecutionSettings(
                service_id=self.service_id,
                temperature=0.7,
                top_p=0.9,
                max_tokens=300
            )
            
            # Get response
            response = await chat_service.get_chat_message_content(
                chat_history=chat_history,
                settings=execution_settings
            )
            
            warning_text = str(response).strip()
            
            # Fallback if response is too short or empty
            if not warning_text or len(warning_text) < 30:
                logger.warning("Warning response too short, using fallback")
                return self._get_fallback_warning(user_name, strikes)
            
            logger.info(f"Generated warning for user {user_name} (strikes: {strikes + 1})")
            return warning_text
            
        except Exception as e:
            logger.error(f"Error generating warning response: {e}", exc_info=True)
            return self._get_fallback_warning(user_name, strikes)
    
    def _get_fallback_warning(self, user_name: str, strikes: int) -> str:
        """Fallback warning messages if generation fails"""
        if strikes >= 2:
            return (
                f"⚠️ {user_name}, that's your final warning.\n\n"
                "I'm here to help with astrology, but I won't tolerate disrespectful language. "
                "One more instance and your account will be suspended.\n\n"
                "Let's keep it respectful, mate. 🌿"
            )
        elif strikes == 1:
            return (
                f"⚠️ Hey {user_name}, I need you to watch your language.\n\n"
                "I'm happy to help you with your cosmic questions, but let's keep things respectful. "
                "This is your second warning.\n\n"
                "Can you rephrase that nicely? 🌿"
            )
        else:
            return (
                f"Hey {user_name}, I hear you're frustrated, but let's keep it respectful, yeah? 🌿\n\n"
                "I'm here to help with your astrology questions, but I need you to communicate politely. "
                "Can you rephrase that and ask again nicely?\n\n"
                "Cheers! ✨"
            )