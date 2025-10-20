"""Command handlers for Telegram bot"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select, delete

from app.database import AsyncSessionLocal
from app.models import User, ChatHistory

logger = logging.getLogger(__name__)

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
        "• Career predictions for this year\n"
        "• What lottery numbers should I play?\n"
        "• Lucky numbers for Powerball this week\n"
        "• Give me 5 sets of lottery numbers for Oz Lotto\n\n"
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
                "Use /start to get started with the setup wizard."
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