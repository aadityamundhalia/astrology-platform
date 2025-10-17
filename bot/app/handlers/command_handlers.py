"""Command handlers for Telegram bot"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select, delete

from app.database import AsyncSessionLocal
from app.models import User, ChatHistory

logger = logging.getLogger(__name__)

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE, telegram_service):
    """Handle /start command"""
    user = update.message.from_user
    user_id = user.id
    
    logger.info(f"👋 User started: {user.first_name} (ID: {user_id})")
    
    # Save/update user in database
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            new_user = User(
                id=user_id,
                is_bot=user.is_bot,
                first_name=user.first_name,
                username=user.username,
                language_code=user.language_code,
                is_premium=user.is_premium or False,
                date=int(update.message.date.timestamp()),
                is_active=True,
                priority=5,
                strikes=0,
                encrypt_chats=False  # Default to no encryption
            )
            db.add(new_user)
            await db.commit()
            logger.info(f"✅ Created new user: {user.first_name}")
            
            # New user - show setup instructions
            welcome_message = (
                f"G'day {user.first_name}! 🌿\n\n"
                "I'm Rudie, your cosmic guide through the stars! ✨\n\n"
                "Before we dive into your astrological journey, I'll need a few details:\n"
                "📅 Date of Birth\n"
                "⏰ Time of Birth\n"
                "📍 Place of Birth\n\n"
                "Use /change to set up your birth details through our step-by-step wizard.\n\n"
                "Or send them all at once like this:\n"
                "Date of Birth: 1990-01-15\n"
                "Time of Birth: 10:30\n"
                "Place of Birth: New Delhi, India\n\n"
                "Once that's sorted, ask me anything about your stars! 🌟\n\n"
                "Use /help to see what I can do for you!"
            )
        else:
            # Existing user - check if they have birth details
            has_birth_data = all([
                existing_user.date_of_birth,
                existing_user.time_of_birth,
                existing_user.place_of_birth
            ])
            
            if has_birth_data:
                # User has complete birth data
                encryption_status = "🔐 (encrypted)" if existing_user.encrypt_chats else ""
                welcome_message = (
                    f"Welcome back, {user.first_name}! 🌿\n\n"
                    f"Great to see you again! Your birth details are all set:\n"
                    f"📅 {existing_user.date_of_birth}\n"
                    f"⏰ {existing_user.time_of_birth}\n"
                    f"📍 {existing_user.place_of_birth}\n"
                    f"{encryption_status}\n\n"
                    f"What would you like to know about your stars today? ✨\n\n"
                    f"**You can ask me:**\n"
                    f"• How is today for me?\n"
                    f"• What's my week looking like?\n"
                    f"• Tell me about my love life\n"
                    f"• Career predictions\n"
                    f"• Or anything else cosmic! 🌟\n\n"
                    f"Use /change to update your details or /help for more options."
                )
            else:
                # User exists but no birth data
                welcome_message = (
                    f"Welcome back, {user.first_name}! 🌿\n\n"
                    "I see you haven't set up your birth details yet.\n\n"
                    "Use /change to set up your birth details through our step-by-step wizard.\n\n"
                    "Or send them all at once like this:\n"
                    "Date of Birth: 1990-01-15\n"
                    "Time of Birth: 10:30\n"
                    "Place of Birth: New Delhi, India\n\n"
                    "Once that's sorted, ask me anything about your stars! 🌟"
                )
    
    await update.message.reply_text(welcome_message)

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = (
        "**How to Use Rudie** 🌿\n\n"
        "**Setup Commands:**\n"
        "/start - Get started or view your details\n"
        "/change - Update your birth details & privacy settings\n"
        "/info - View your current details\n"
        "/clear - Clear your chat history\n\n"
        "**Ask Me Anything:**\n"
        "• How is today for me?\n"
        "• What's my week looking like?\n"
        "• Tell me about my love life\n"
        "• Should I take this job offer?\n"
        "• Career predictions for this year\n\n"
        "**Privacy & Security:**\n"
        "🔐 You can enable chat encryption via /change\n"
        "• Encrypts your messages in our database\n"
        "• Extra layer of privacy\n"
        "• Can be enabled/disabled anytime\n\n"
        "Just chat with me naturally and I'll read the stars for you! ✨"
    )
    
    await update.message.reply_text(help_message)

async def handle_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command - show user's birth details and settings"""
    user_id = update.message.from_user.id
    
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            await update.message.reply_text(
                "I don't have your details yet! Use /start to get started."
            )
            return
        
        # Check if birth data is complete
        has_birth_data = all([
            user.date_of_birth,
            user.time_of_birth,
            user.place_of_birth
        ])
        
        if has_birth_data:
            encryption_status = "🔐 Enabled" if user.encrypt_chats else "📝 Disabled"
            
            info_message = (
                f"**Your Profile** 👤\n\n"
                f"**Birth Details:**\n"
                f"📅 Date: {user.date_of_birth}\n"
                f"⏰ Time: {user.time_of_birth}\n"
                f"📍 Place: {user.place_of_birth}\n\n"
                f"**Settings:**\n"
                f"🔐 Chat Encryption: {encryption_status}\n"
                f"⚡ Priority: {user.priority}\n"
                f"✅ Status: {'Active' if user.is_active else 'Inactive'}\n"
                f"⚠️ Strikes: {user.strikes}\n\n"
                f"Use /change to update your details or privacy settings."
            )
        else:
            info_message = (
                "You haven't set up your birth details yet! 🌟\n\n"
                "Use /change to get started with the setup wizard."
            )
        
        await update.message.reply_text(info_message)

async def handle_clear(update: Update, context: ContextTypes.DEFAULT_TYPE, telegram_service, memory_service):
    """Handle /clear command - clear chat history and memory"""
    user_id = update.message.from_user.id
    
    try:
        # Clear from database
        async with AsyncSessionLocal() as db:
            stmt = delete(ChatHistory).where(ChatHistory.user_id == user_id)
            await db.execute(stmt)
            await db.commit()
        
        # Clear from Redis
        telegram_service.clear_redis_history(user_id)
        
        # Clear from Mem0
        try:
            await memory_service.clear_memory(user_id)
        except Exception as e:
            logger.warning(f"Could not clear Mem0 memory: {e}")
        
        await update.message.reply_text(
            "All cleared! 🧹\n\n"
            "Your chat history and memories have been wiped clean.\n"
            "Feel free to start fresh! 🌟"
        )
        
        logger.info(f"🧹 Cleared history for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error clearing history: {e}", exc_info=True)
        await update.message.reply_text(
            "Oops! Something went wrong clearing your history. Please try again!"
        )