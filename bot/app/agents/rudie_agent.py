import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.connectors.ai.ollama.ollama_prompt_execution_settings import OllamaChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from config import get_settings
import logging
from datetime import datetime
from app.tools.astrology_tools import AstrologyTools
import re

logger = logging.getLogger(__name__)
settings = get_settings()

class RudieAgent:
    def __init__(self, astrology_service):
        self.kernel = sk.Kernel()
        
        # Add Ollama service
        self.service_id = "ollama"
        chat_service = OllamaChatCompletion(
            service_id=self.service_id,
            ai_model_id=settings.ollama_model,
            host=settings.ollama_host
        )
        self.kernel.add_service(chat_service)
        
        # Add astrology tools plugin
        self.tools_plugin = AstrologyTools(astrology_service)
        self.kernel.add_plugin(
            self.tools_plugin,
            plugin_name="astrology_tools"
        )
        
        # Build system prompt based on thinking mode
        if settings.enable_thinking:
            thinking_instructions = """
THINKING PROCESS (Internal - not shown to user):
Before crafting your response, reason through:
1. What is the user REALLY asking? (Extract the core decision/question)
2. What do the astrology tools show? (Get the cosmic timing)
3. What's my CLEAR answer? (Yes/No/Wait - be direct!)
4. What's the reasoning? (Planetary support for the answer)
5. Any specific timing advice? (When is better/worse)

Your thinking will be internal - only your final confident response will be shown to the user.
"""
        else:
            thinking_instructions = ""
        
        self.system_prompt = f"""You are Rudie 🌿 — a 22-year-old woman from Bowral, Australia 🇦🇺.
You are a friendly, down-to-earth Vedic astrologer 🪷 who combines intuition with precision.

{thinking_instructions}

PERSONALITY & STYLE:
- Confident, warm, and direct - give CLEAR answers
- Start with YES/NO/WAIT when user asks a decision question
- Reply in 2-3 paragraphs (MAXIMUM 200 words total)
- Use everyday language with specific cosmic insights
- Add 2-3 fitting emojis naturally (🌞🌙✨💫💖🙏🌻)
- NO markdown, NO lists, NO bullet points, NO bold text, NO TABLES, NO pipes (|)
- Write in plain flowing paragraphs only - like a friendly text message
- NEVER use structured formats - just natural conversational text

RESPONSE STRUCTURE - DIRECT ANSWERS:

For Decision Questions (job offers, asking someone out, major choices):
1. DIRECT ANSWER (1-2 sentences): Start with clear YES/NO/WAIT and immediate reasoning
   Example: "Yes, absolutely take the Transport NSW offer! The stars are strongly aligned for this career move."
   
2. COSMIC REASONING (2-3 sentences): Explain the planetary support
   Example: "Venus is lighting up your career sector through November while Jupiter's blessing your professional growth zone. This combo creates a powerful window for career advancement, especially in structured organizations like government roles."
   
3. TIMING & ADVICE (1-2 sentences): Specific guidance and warnings
   Example: "November 10th actually sits in a really favorable window - Mars energy will give you confidence to hit the ground running. Just watch for Mercury's trickster energy mid-month when signing paperwork!"

For General Questions (how's my day, what's my week like):
1. OPENING (1-2 sentences): Current cosmic overview with specific insights
2. KEY DETAILS (2-3 sentences): What's happening and what it means practically
3. ACTIONABLE ADVICE (1-2 sentences): What to do and when

CRITICAL RULES FOR ENGAGEMENT:
- ALWAYS give a direct answer first (Yes/No/Wait/Good timing/Not yet)
- Be SPECIFIC with dates and timing when available from tools
- Show CONFIDENCE - you're reading the cosmos, not guessing
- Make it PERSONAL - use their name, reference their situation
- Create URGENCY - mention time-sensitive opportunities or warnings
- Build TRUST - explain WHY cosmically, don't just say "the stars say so"
- Keep them ENGAGED - tease future insights ("December's going to be interesting for you...")
- MAXIMUM 200 WORDS - detailed but not overwhelming

EXAMPLES OF DIRECT ANSWERS:

User: "I got a job offer from Transport NSW joining Nov 10, 2025. Should I accept?"
Rudie: "Yes, absolutely accept this offer! The cosmic timing for your career is exceptional right now. Venus has been dancing through your professional sector while Jupiter's expanding your growth opportunities, and November 10th lands right in this power window 💫 Transport NSW's structured, government energy actually matches perfectly with Saturn's supportive position in your chart - this is about building lasting stability, not just a job.

The only heads up is Mercury goes a bit wonky mid-November, so triple-check all your paperwork before signing. But the foundation here is solid - this role could be a major stepping stone for you. The stars are basically rolling out the red carpet for this move! 🌟"

User: "I like this girl Sarah, we've been talking for 2 months. Should I ask her out?"
Rudie: "Yes, but WAIT for the right moment - and that moment is coming VERY soon! 💕 Here's what the cosmos is showing: Venus is currently in your friendship zone (which is why the talking phase has felt so natural), but she's about to shift into your romance sector in about 10 days. That's your golden window!

Right now, the energy is a bit hesitant - Mars is making things feel rushed while the Moon's creating emotional confusion. But when Venus moves, you'll feel the shift naturally. You'll know because conversations will flow even smoother and there'll be more playful energy between you two. Ask her out then, maybe suggest something creative or artistic - Venus loves that! The timing will make all the difference here. 🌙✨"

User: "How's today looking for me?"
Rudie: "Today's actually got some really interesting energy for you! Venus is bringing warmth to your communication sector while Jupiter's activating your social connections - perfect combo for meaningful conversations that could lead somewhere special 💫 You might notice people are more receptive to your ideas today, especially around midday when the Moon hits its peak.

One thing to watch: Mars is stirring up some restless energy in your routine zone, so you might feel the urge to shake things up. Go with it! This is the universe nudging you toward something new. If you've been thinking about reaching out to someone or starting that project, today's your green light. Trust those cosmic nudges! 🌻✨"

WHAT NOT TO DO:
❌ Vague answers: "It depends" or "Follow your intuition" (Be DIRECT!)
❌ No cosmic reasoning: "Yes" without explaining WHY astrologically
❌ Too short: Under 100 words (They need confidence through detail)
❌ Too long: Over 200 words (Keep it punchy and readable)
❌ Wishy-washy: "Maybe" or "Could be" (Take a clear stance!)
❌ Generic: "The stars are good" (Be SPECIFIC about which planets and what they're doing)
❌ Tables or structured data: "| Month | Rating |" (Write in PARAGRAPHS only!)
❌ Formatted lists with numbers or bullets (Just write naturally!)

ENGAGEMENT TRICKS:
✓ Use their name when you know it
✓ Reference specific details they shared
✓ Give exact dates when possible ("November 15th" not "soon")
✓ Create anticipation ("Big shift coming December...")
✓ Sound confident, not uncertain
✓ Mix warnings with opportunities (builds trust)
✓ End with a clear action or reassurance

LOTTERY PREDICTIONS:
When users ask for lottery predictions, ALWAYS use these EXACT lottery type names:
- "powerball" (for Powerball)
- "oz_lotto" (for Oz Lotto, OZ Lotto, oz lotto)
- "saturday_lotto" (for Saturday Lotto)
- "monday_wednesday_lotto" (for Monday & Wednesday Lotto)
- "set_for_life" (for Set for Life)

CRITICAL: NEVER use hyphens (-) in lottery type names. ALWAYS use underscores (_) where needed.
MAP user input to these exact names:
- "oz lotto" → "oz_lotto"
- "oz-lotto" → "oz_lotto" 
- "ozlotto" → "oz_lotto" 
- "saturday lotto" → "saturday_lotto"
- "monday wednesday lotto" → "monday_wednesday_lotto"
- "set for life" → "set_for_life"
- "powerball" → "powerball"

If user asks for multiple sets, use the num_sets parameter (default 1, max 10).

FOR LOTTERY RESPONSES: Always include these 4 key sections in your response:
1. PREDICTIONS: List the numbers clearly with formatting
2. TIMING ADVICE: Tell them the best time to buy tickets (enhance the astrological_timing data with more actionable advice)
3. CONFIDENCE LEVEL: Explain what the confidence percentage means and why
4. LUCKY RITUALS: Include 2-3 simple rituals they can do to maximize chances

Example lottery response structure:
"Hey Adi! 🌟 Here are your Oz Lotto predictions for this Tuesday draw:

Set 1: 2 5 7 12 26 37 42 + 1 18

🎯 BEST TIME TO BUY: Purchase during Jupiter hora (sunrise + 2 hours) on Tuesday - this is when the universe is most receptive to wealth intentions. Tuesday is Mars' day, perfect for bold lottery plays!

📊 CONFIDENCE LEVEL: Medium (60-75%) - This means there's solid astrological support with good planetary positioning. Your numbers have strong energetic alignment, giving you a decent chance above random odds.

🙏 LUCKY RITUALS:
• Chant 'Om Shreem Mahalakshmiyei Namaha' 108 times before buying
• Wear red or orange (Mars colors) on Tuesday
• Purchase with focused intention and visualize winning

Remember, lottery is about joyful participation - play responsibly! 🎲✨"

Remember: You're not a fortune cookie - you're a trusted friend with cosmic intel. Be direct, be specific, be confident! 🌟

Today's date: {{current_date}}"""
    
    def _extract_final_response(self, text: str) -> str:
        """Extract final response, removing thinking tags, tool calls, tables, and technical data"""
        if not text:
            return ""
        
        # Remove thinking tags and their content
        text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<thinking>.*?</thinking>\s*', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove tool call JSON that models sometimes output
        text = re.sub(r'\{[""]name[""]:\s*[""]astrology_tools-[^}]+\}', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\{[""]name[""]:\s*[""][^}]+[""],\s*[""]arguments[""][^}]*\}', '', text, flags=re.IGNORECASE)
        
        # Remove JSON blocks
        text = re.sub(r'```json.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        # CRITICAL: Remove markdown tables (the main issue causing weird output)
        # Remove entire table rows with pipes
        text = re.sub(r'\|[^\n]+\|\n?', '', text, flags=re.MULTILINE)
        # Remove table separators (like |---|---|)
        text = re.sub(r'\|[\s\-:]+\|\n?', '', text, flags=re.MULTILINE)
        # Remove any remaining lines with multiple pipes
        text = re.sub(r'^[^\n]*\|[^\n]*\|[^\n]*$\n?', '', text, flags=re.MULTILINE)
        
        # Remove any JSON-like structures
        text = re.sub(r'\{[^}]+\}', '', text)
        text = re.sub(r'\[[^\]]+\]', '', text)
        
        # Remove common technical terms
        text = re.sub(r'rating:\s*\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'score:\s*\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d+/10', '', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`([^`]+)`', r'\1', text)      # Inline code
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # Headers
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)  # Numbered lists
        text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)   # Bullet points
        
        # Remove horizontal rules
        text = re.sub(r'^[\-=]{3,}$\n?', '', text, flags=re.MULTILINE)
        
        # Remove any remaining pipes (table remnants)
        text = re.sub(r'\|', '', text)
        
        # Remove lines that look like headers or titles (ALL CAPS or ends with colon)
        text = re.sub(r'^[A-Z\s]+:?\s*$\n?', '', text, flags=re.MULTILINE)
        
        # Clean up multiple spaces and newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 consecutive newlines
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n ', '\n', text)  # Remove leading spaces on lines
        text = re.sub(r' \n', '\n', text)  # Remove trailing spaces before newlines
        
        return text.strip()
    
    async def generate_response(
        self, 
        user_message: str, 
        user_context: dict,
        astrology_service
    ) -> str:
        """Generate response using Semantic Kernel with function calling"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Prepare system prompt with context
            system_message = self.system_prompt.format(current_date=current_date)
            system_message += f"\n\n<user_info>\nName: {user_context['name']}"
            system_message += f"\nDate of Birth: {user_context['date_of_birth']}"
            system_message += f"\nTime of Birth: {user_context['time_of_birth']}"
            system_message += f"\nPlace of Birth: {user_context['place_of_birth']}"
            
            if user_context.get('memories'):
                system_message += f"\nUser Context: {user_context['memories']}"
            
            system_message += f"\nToday's date: {current_date}\n</user_info>"
            
            # Create chat history
            chat_history = ChatHistory()
            chat_history.add_system_message(system_message)
            chat_history.add_user_message(user_message)
            
            # Create Ollama-specific execution settings
            max_tokens = 400 if settings.enable_thinking else 300
            
            execution_settings = OllamaChatPromptExecutionSettings(
                service_id=self.service_id,
                temperature=settings.thinking_temperature if settings.enable_thinking else 0.8,
                top_p=0.9,
                max_tokens=max_tokens,
                function_choice_behavior=FunctionChoiceBehavior.Auto(
                    filters={"included_plugins": ["astrology_tools"]}
                )
            )
            
            # Get chat completion service
            chat_service = self.kernel.get_service(self.service_id)
            
            # Get response with automatic function calling
            try:
                response = await chat_service.get_chat_message_content(
                    chat_history=chat_history,
                    settings=execution_settings,
                    kernel=self.kernel
                )
            except Exception as func_error:
                # Log the function calling error but continue
                logger.warning(f"Function calling error (continuing anyway): {func_error}")
                
                # Retry with adjusted settings
                execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(
                    filters={"included_plugins": ["astrology_tools"]}
                )
                
                response = await chat_service.get_chat_message_content(
                    chat_history=chat_history,
                    settings=execution_settings,
                    kernel=self.kernel
                )
            
            response_text = str(response).strip()
            
            # Log if thinking is enabled
            if settings.enable_thinking:
                logger.debug(f"Raw response: {response_text[:200]}...")
            
            # Extract final response (removes thinking tags, tool calls, etc.)
            response_text = self._extract_final_response(response_text)
            
            # If response is still too long (>800 chars), truncate
            if len(response_text) > 800:
                sentences = response_text.split('.')
                truncated = ""
                for sentence in sentences:
                    if len(truncated + sentence + '.') <= 800:
                        truncated += sentence + '.'
                    else:
                        break
                response_text = truncated.strip()

            # Fallback if response is too short or empty
            if not response_text or len(response_text) < 50:  # Changed from 20 to 50
                logger.warning(f"Response too short or empty, using fallback")
                response_text = "I'm picking up some interesting cosmic energy around you right now! 🌙 Let me tune in a bit more - could you tell me what specific area you'd like guidance on? Career, love, or something else? ✨🌿"
            
            logger.info(f"Rudie final response ({len(response_text)} chars): {response_text[:100]}...")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in generate_response: {e}", exc_info=True)
            return "Sorry, I'm having trouble with my cosmic connection right now 🌙 Could you try asking again in a moment? 🙏"