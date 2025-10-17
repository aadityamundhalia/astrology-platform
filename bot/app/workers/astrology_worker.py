"""Worker that processes astrology requests from the queue"""
import logging
import asyncio
import re

from app.database import AsyncSessionLocal
from app.models import User
from app.utils.profanity_filter import is_rude_or_aggressive
from config import get_settings
from sqlalchemy import select

logger = logging.getLogger(__name__)
settings = get_settings()

class AstrologyWorker:
    def __init__(
        self,
        telegram_service,
        memory_service,
        astrology_service,
        rudie_agent
    ):
        self.telegram_service = telegram_service
        self.memory_service = memory_service
        self.astrology_service = astrology_service
        self.rudie_agent = rudie_agent
    
    async def process_request(self, request_data: dict):
        """Process a single astrology request"""
        try:
            # Validate required fields
            required_fields = ['user_id', 'chat_id', 'message', 'user_context']
            missing_fields = [field for field in required_fields if field not in request_data]
            
            if missing_fields:
                logger.warning(f"⚠️ Skipping malformed message - missing fields: {missing_fields}")
                logger.debug(f"Message data: {request_data}")
                return
            
            # Validate user_context
            required_context = ['name', 'date_of_birth', 'time_of_birth', 'place_of_birth']
            user_context = request_data.get('user_context', {})
            missing_context = [field for field in required_context if field not in user_context]
            
            if missing_context:
                logger.warning(f"⚠️ Skipping message - missing user context: {missing_context}")
                return
            
            user_id = request_data['user_id']
            chat_id = request_data['chat_id']
            text = request_data['message']
            
            # Check if user has encryption enabled for logging
            async with AsyncSessionLocal() as db:
                stmt = select(User).where(User.id == user_id)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                
                should_encrypt = user and user.encrypt_chats
                
                # Conditional logging
                if should_encrypt:
                    logger.info(f"🔮 Processing encrypted query for user {user_id}")
                else:
                    logger.info(f"🔮 Processing astrology query for user {user_id}: {text[:50]}...")

            request_id = request_data.get('request_id', 'unknown')
            
            # Skip test messages
            if isinstance(text, str) and ('test' in text.lower() or 'batch_test' in text.lower()):
                logger.info(f"⏭️ Skipping test message: {request_id}")
                return
            
            # Check for profanity/rudeness if enabled
            if settings.enable_profanity_filter:
                is_rude, reason = is_rude_or_aggressive(text)
                
                if is_rude:
                    logger.warning(f"⚠️ Rude message detected from user {user_id}: {reason}")
                    
                    # Update user strikes
                    async with AsyncSessionLocal() as db:
                        stmt = select(User).where(User.id == user_id)
                        result = await db.execute(stmt)
                        user = result.scalar_one_or_none()
                        
                        if user:
                            user.strikes += 1
                            current_strikes = user.strikes
                            
                            # Check if max strikes reached
                            if current_strikes >= settings.max_strikes:
                                user.is_active = False
                                await db.commit()
                                
                                logger.warning(f"🚫 User {user_id} deactivated - max strikes reached ({current_strikes}/{settings.max_strikes})")
                                
                                response = f"""🚫 **Account Deactivated**

I've had to deactivate your account due to repeated inappropriate behavior ({current_strikes} strikes).

Respectful communication is important to me. If you'd like to appeal this decision, please contact support.

Take care! 🌿"""
                                
                                await self.telegram_service.send_message(chat_id, response)
                                return
                            else:
                                await db.commit()
                                
                                logger.info(f"⚠️ Strike added to user {user_id}: {current_strikes}/{settings.max_strikes}")
                                
                                remaining = settings.max_strikes - current_strikes
                                response = f"""⚠️ **Strike {current_strikes}/{settings.max_strikes}**

Hey, I understand you might be frustrated, but I don't appreciate that kind of language. I'm here to help you with genuine cosmic guidance, and I'd really appreciate if we could keep our conversation respectful 🌿

You have {remaining} warning{'s' if remaining != 1 else ''} remaining. If you reach {settings.max_strikes} strikes, your account will be automatically deactivated.

Let's start fresh - what would you like to know about your stars? ✨"""
                                
                                await self.telegram_service.send_message(chat_id, response)
                                return
            
            # Send typing indicator
            stop_typing = asyncio.Event()
            typing_task = asyncio.create_task(
                self.telegram_service.keep_typing(chat_id, stop_typing)
            )
            
            try:
                logger.info(f"🔮 Processing astrology query for user {user_id}")
                
                # Get memories
                try:
                    memories_result = await self.memory_service.get_memories(user_id, text)
                    memory_data = ""
                    
                    if memories_result and isinstance(memories_result, dict):
                        memory_data = memories_result.get("data", "")
                    else:
                        logger.warning(f"🧠 Invalid memories result: {type(memories_result)}")
                        memory_data = ""
                        
                except Exception as e:
                    logger.warning(f"🧠 Failed to get memories, continuing without: {e}")
                    memory_data = ""
                
                # Add memories to context
                user_context['memories'] = memory_data
                
                # Generate response using Rudie agent
                response = await self.rudie_agent.generate_response(
                    user_message=text,
                    user_context=user_context,
                    astrology_service=self.astrology_service
                )
                
                # Clean response
                response = re.sub(r'<think>.*?</think>\s*', '', response, flags=re.DOTALL)
                response = response.strip()
                
                # Stop typing
                stop_typing.set()
                if typing_task:
                    await typing_task
                
                # Send response
                await self.telegram_service.send_message(chat_id, response)
                
                # Save to database and Redis
                async with AsyncSessionLocal() as db:
                    await self.telegram_service.save_chat_to_db(db, user_id, "user", text)
                    await self.telegram_service.save_chat_to_db(db, user_id, "bot", response)
                
                self.telegram_service.save_chat_to_redis(user_id, "user", text)
                self.telegram_service.save_chat_to_redis(user_id, "bot", response)
                
                # Add to memory (in background)
                async def add_memory_safe():
                    try:
                        await self.memory_service.add_memory(user_id, text, response)
                    except Exception as e:
                        logger.error(f"Failed to add memory: {e}")
                
                asyncio.create_task(add_memory_safe())
                
                logger.info(f"✅ Completed request {request_id} for user {user_id}")
                
            except Exception as e:
                logger.error(f"❌ Error processing request {request_id}: {e}", exc_info=True)
                
                stop_typing.set()
                if typing_task:
                    try:
                        await typing_task
                    except:
                        pass
                
                try:
                    await self.telegram_service.send_message(
                        chat_id,
                        "Sorry, I had trouble reading the stars for you. Please try again! 🌿"
                    )
                except:
                    pass
            finally:
                stop_typing.set()
                if typing_task and not typing_task.done():
                    try:
                        await typing_task
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"❌ Fatal error in process_request: {e}", exc_info=True)