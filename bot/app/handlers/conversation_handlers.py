"""Conversation handlers for birth details collection"""
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import User

logger = logging.getLogger(__name__)

# Conversation states
DOB, TOB, POB, ENCRYPTION = range(4)  # Add ENCRYPTION state

async def change_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the birth details collection wizard"""
    await update.message.reply_text(
        "Let's update your birth details! 🌟\n\n"
        "First, what's your date of birth?\n"
        "Format: YYYY-MM-DD (e.g., 1990-01-15)\n\n"
        "Send /cancel anytime to stop."
    )
    return DOB

async def receive_dob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive date of birth"""
    dob = update.message.text.strip()
    
    # Basic validation
    import re
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', dob):
        await update.message.reply_text(
            "Invalid format! Please use YYYY-MM-DD format.\n"
            "Example: 1990-01-15"
        )
        return DOB
    
    context.user_data['date_of_birth'] = dob
    
    await update.message.reply_text(
        "Got it! ✅\n\n"
        "Now, what time were you born?\n"
        "Format: HH:MM (24-hour format, e.g., 14:30)\n"
        "If you don't know the exact time, use 12:00"
    )
    return TOB

async def receive_tob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive time of birth"""
    tob = update.message.text.strip()
    
    # Basic validation
    import re
    if not re.match(r'^\d{1,2}:\d{2}$', tob):
        await update.message.reply_text(
            "Invalid format! Please use HH:MM format.\n"
            "Example: 14:30 or 09:15"
        )
        return TOB
    
    context.user_data['time_of_birth'] = tob
    
    await update.message.reply_text(
        "Perfect! ✅\n\n"
        "Finally, where were you born?\n"
        "Format: City, State/Region\n"
        "Example: New Delhi, India"
    )
    return POB

async def receive_pob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive place of birth and ask about encryption"""
    pob = update.message.text.strip()
    
    if len(pob) < 3:
        await update.message.reply_text(
            "Please provide a valid location.\n"
            "Example: New Delhi, India"
        )
        return POB
    
    context.user_data['place_of_birth'] = pob
    
    # Ask about encryption
    keyboard = [['Yes, encrypt my chats 🔐'], ['No, keep them unencrypted']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "Great! ✅\n\n"
        "🔐 **Privacy Option**\n\n"
        "Would you like to encrypt your chat messages?\n\n"
        "**Benefits of encryption:**\n"
        "• Your messages are encrypted in our database\n"
        "• Extra layer of privacy protection\n"
        "• Your chats won't appear in logs\n\n"
        "**Note:** This only affects message storage, not functionality.",
        reply_markup=reply_markup
    )
    return ENCRYPTION

async def receive_encryption_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive encryption preference and save all details"""
    user_id = update.message.from_user.id
    choice = update.message.text.strip()
    
    # Determine encryption preference
    encrypt_chats = 'yes' in choice.lower() or '🔐' in choice
    
    try:
        async with AsyncSessionLocal() as db:
            # Get user
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                await update.message.reply_text(
                    "Something went wrong. Please try /start first.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return ConversationHandler.END
            
            # Check if encryption preference changed
            old_encrypt = user.encrypt_chats
            new_encrypt = encrypt_chats
            
            # Update user details
            user.date_of_birth = context.user_data['date_of_birth']
            user.time_of_birth = context.user_data['time_of_birth']
            user.place_of_birth = context.user_data['place_of_birth']
            user.encrypt_chats = encrypt_chats
            
            await db.commit()
            
            # If encryption preference changed, handle existing chats
            if old_encrypt != new_encrypt:
                if new_encrypt:
                    # User enabled encryption - encrypt all existing unencrypted chats
                    await encrypt_user_chats(user_id, db)
                    encryption_msg = "✅ Encryption enabled! All your previous chats have been encrypted."
                else:
                    # User disabled encryption - leave encrypted chats as is
                    encryption_msg = "✅ Encryption disabled for future chats. Previous encrypted chats remain encrypted."
            else:
                if new_encrypt:
                    encryption_msg = "🔐 Encryption enabled for your chats."
                else:
                    encryption_msg = "📝 Your chats will be stored unencrypted."
            
            await update.message.reply_text(
                f"All set! 🎉\n\n"
                f"**Your Details:**\n"
                f"📅 Date of Birth: {user.date_of_birth}\n"
                f"⏰ Time of Birth: {user.time_of_birth}\n"
                f"📍 Place of Birth: {user.place_of_birth}\n\n"
                f"{encryption_msg}\n\n"
                f"Now ask me anything about your stars! ✨",
                reply_markup=ReplyKeyboardRemove()
            )
            
    except Exception as e:
        logger.error(f"Error saving birth details: {e}", exc_info=True)
        await update.message.reply_text(
            "Sorry, there was an error saving your details. Please try again!",
            reply_markup=ReplyKeyboardRemove()
        )
    
    return ConversationHandler.END

async def encrypt_user_chats(user_id: int, db):
    """Encrypt all unencrypted chats for a user"""
    from sqlalchemy import update
    from app.models import ChatHistory
    from app.utils.encryption import get_encryption
    
    try:
        encryption = get_encryption()
        
        # Get all unencrypted chats for this user
        stmt = select(ChatHistory).where(
            ChatHistory.user_id == user_id,
            ChatHistory.is_encrypted == False
        )
        result = await db.execute(stmt)
        chats = result.scalars().all()
        
        logger.info(f"Encrypting {len(chats)} unencrypted chats for user {user_id}")
        
        # Encrypt each chat
        for chat in chats:
            encrypted_message = encryption.encrypt(chat.message)
            chat.message = encrypted_message
            chat.is_encrypted = True
        
        await db.commit()
        logger.info(f"Successfully encrypted {len(chats)} chats for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error encrypting user chats: {e}", exc_info=True)
        await db.rollback()

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text(
        "Cancelled! You can use /change anytime to update your details.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Create conversation handler
birth_details_conversation = ConversationHandler(
    entry_points=[CommandHandler('change', change_command)],
    states={
        DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_dob)],
        TOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tob)],
        POB: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_pob)],
        ENCRYPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_encryption_preference)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    name="birth_details_conversation",
    persistent=False
)