"""Main message handler for astrology queries"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
import asyncio
import re
import uuid

from app.database import AsyncSessionLocal
from app.models import User
from app.utils.validators import validate_birth_data

logger = logging.getLogger(__name__)

async def handle_message(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE,
    telegram_service,
    queue_service,
    extraction_agent
):
    """Handle incoming telegram messages - publish to queue"""
    stop_typing = asyncio.Event()
    typing_task = None
    
    try:
        message = update.message
        user_id = message.from_user.id
        chat_id = message.chat.id
        text = message.text
        
        logger.info(f"📥 Telegram received: user {user_id} - {len(text)} chars: {text}")
        
        typing_task = asyncio.create_task(
            telegram_service.keep_typing(chat_id, stop_typing)
        )
        
        async with AsyncSessionLocal() as db:
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    id=user_id,
                    is_bot=message.from_user.is_bot,
                    first_name=message.from_user.first_name,
                    username=message.from_user.username,
                    language_code=message.from_user.language_code,
                    is_premium=message.from_user.is_premium or False,
                    date=int(message.date.timestamp()),
                    is_active=True,  # Default active
                    priority=5  # Default priority
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"🚫 User {user_id} is inactive - rejecting request")
                
                stop_typing.set()
                if typing_task:
                    await typing_task
                
                response = "⚠️ Your account is currently inactive. Please contact support if you believe this is an error."
                await telegram_service.send_message(chat_id, response)
                return
            
            has_birth_data = validate_birth_data(
                user.date_of_birth, 
                user.time_of_birth, 
                user.place_of_birth
            )
            
            if not has_birth_data:
                logger.info(f"🔍 User {user_id} missing birth data, attempting extraction...")
                
                extracted = await extraction_agent.extract_birth_data(text)
                
                if extracted and all([
                    extracted.get("date_of_birth"),
                    extracted.get("time_of_birth"),
                    extracted.get("place_of_birth")
                ]):
                    user.date_of_birth = extracted["date_of_birth"]
                    user.time_of_birth = extracted["time_of_birth"]
                    user.place_of_birth = extracted["place_of_birth"]
                    await db.commit()
                    
                    logger.info(f"✅ Extracted and saved birth data for user {user_id}")
                    
                    stop_typing.set()
                    if typing_task:
                        await typing_task
                    
                    response = "Thanks for sharing your details 🌿\nWhat would you like me to look into for you today? 🌞"
                    await telegram_service.send_message(chat_id, response)
                    return
                else:
                    logger.warning(f"⚠️ Extraction failed for user {user_id}, asking for details...")
                    
                    stop_typing.set()
                    if typing_task:
                        await typing_task
                    
                    response = ("Please provide your birth details in this exact format:\n\n"
                               "Date of Birth: 1970-11-22\n"
                               "Time of Birth: 00:25\n"
                               "Place of Birth: Hisar, Haryana\n\n"
                               "Or use /change for the step-by-step wizard!")
                    await telegram_service.send_message(chat_id, response)
                    return
            
            logger.info(f"✅ User {user_id} (priority: {user.priority}) has birth data, queuing request...")
            
            # Publish request to queue with priority
            request_id = str(uuid.uuid4())
            request_data = {
                'request_id': request_id,
                'user_id': user_id,
                'chat_id': chat_id,
                'message': text,
                'priority': user.priority,  # Include priority
                'user_context': {
                    'name': user.first_name,
                    'date_of_birth': user.date_of_birth,
                    'time_of_birth': user.time_of_birth,
                    'place_of_birth': user.place_of_birth
                }
            }
            
            await queue_service.publish_request(request_data)
            
            stop_typing.set()
            if typing_task:
                await typing_task
            
            # Send message based on priority
            if user.priority <= 2:
                position_msg = "⚡ Priority user - reading the stars for you now... ✨"
            else:
                position_msg = "🔮 Reading the stars for you... ✨"
            
            await telegram_service.send_message(chat_id, position_msg)
            
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        
        stop_typing.set()
        if typing_task:
            try:
                await typing_task
            except:
                pass
        
        try:
            await telegram_service.send_message(
                chat_id,
                "Sorry, something went wrong. Please try again! 🌿"
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