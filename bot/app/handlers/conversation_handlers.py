"""Conversation handlers for birth details collection"""
import logging
from datetime import datetime
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
DOB, TOB, POB, ENCRYPTION = range(4)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command and check if user needs setup"""
    user = update.message.from_user
    user_id = user.id
    
    logger.info(f"👋 [CONVERSATION HANDLER] User started: {user.first_name} (ID: {user_id})")
    
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            # Create new user
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
                encrypt_chats=False
            )
            db.add(new_user)
            await db.commit()
            logger.info(f"✅ Created new user: {user.first_name}")
            
            # New user - start wizard asking for date of birth
            await update.message.reply_text(
                f"G'day {user.first_name}! 🌿\n\n"
                "I'm Rudie, your cosmic guide through the stars! ✨\n\n"
                "Before we dive into your astrological journey, I'll need a few details. "
                "Let's get you set up!\n\n"
                "First, what's your **date of birth**?\n"
                "📅 Format: YYYY-MM-DD (e.g., 1990-01-15)\n\n"
                "Send /cancel anytime to stop."
            )
            return DOB  # Start wizard from DOB state
            
        else:
            # Check if user has birth details
            has_birth_data = all([
                existing_user.date_of_birth,
                existing_user.time_of_birth,
                existing_user.place_of_birth
            ])
            
            if not has_birth_data:
                # Existing user without birth data - start wizard
                await update.message.reply_text(
                    f"Welcome back, {user.first_name}! 🌿\n\n"
                    "I see you haven't set up your birth details yet. Let's do that now!\n\n"
                    "What's your **date of birth**?\n"
                    "📅 Format: YYYY-MM-DD (e.g., 1990-01-15)\n\n"
                    "Send /cancel anytime to stop."
                )
                return DOB  # Start wizard from DOB state
            else:
                # User has complete birth data - show welcome back message
                encryption_status = "🔐 (encrypted)" if existing_user.encrypt_chats else ""
                await update.message.reply_text(
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
                return ConversationHandler.END  # Don't start wizard

async def change_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the birth details collection wizard"""
    await update.message.reply_text(
        "Let's update your birth details! 🌟\n\n"
        "First, what's your **date of birth**?\n"
        "📅 Format: YYYY-MM-DD (e.g., 1990-01-15)\n\n"
        "Send /cancel anytime to stop."
    )
    return DOB

async def receive_dob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate date of birth"""
    dob = update.message.text.strip()
    
    # Validate format
    import re
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', dob):
        await update.message.reply_text(
            "❌ Invalid format!\n\n"
            "Please use **YYYY-MM-DD** format.\n"
            "📅 Example: 1990-01-15\n\n"
            "Try again:"
        )
        return DOB
    
    # Validate date is real and not in future
    try:
        year, month, day = map(int, dob.split('-'))
        date_obj = datetime(year, month, day)
        
        # Check if date is in the future
        if date_obj > datetime.now():
            await update.message.reply_text(
                "❌ That date is in the future!\n\n"
                "Please enter your actual date of birth.\n"
                "📅 Format: YYYY-MM-DD\n\n"
                "Try again:"
            )
            return DOB
        
        # Check if date is too old (before 1900)
        if year < 1900:
            await update.message.reply_text(
                "❌ That date seems too old!\n\n"
                "Please enter a valid date of birth.\n"
                "📅 Format: YYYY-MM-DD\n\n"
                "Try again:"
            )
            return DOB
            
    except ValueError:
        await update.message.reply_text(
            "❌ That's not a valid date!\n\n"
            "Please check your day and month are correct.\n"
            "📅 Format: YYYY-MM-DD\n"
            "📅 Example: 1990-01-15\n\n"
            "Try again:"
        )
        return DOB
    
    context.user_data['date_of_birth'] = dob
    
    await update.message.reply_text(
        "Got it! ✅\n\n"
        "Now, what **time** were you born?\n"
        "⏰ Format: HH:MM (24-hour format)\n"
        "📝 Example: 14:30 or 09:15\n\n"
        "💡 If you don't know the exact time, use 12:00"
    )
    return TOB

async def receive_tob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate time of birth"""
    tob = update.message.text.strip()
    
    # Validate format
    import re
    if not re.match(r'^\d{1,2}:\d{2}$', tob):
        await update.message.reply_text(
            "❌ Invalid format!\n\n"
            "Please use **HH:MM** format (24-hour).\n"
            "⏰ Example: 14:30 or 09:15\n\n"
            "Try again:"
        )
        return TOB
    
    # Validate time is real
    try:
        hour, minute = map(int, tob.split(':'))
        
        if hour < 0 or hour > 23:
            await update.message.reply_text(
                "❌ Invalid hour!\n\n"
                "Hours must be between 00 and 23.\n"
                "⏰ Example: 14:30 (for 2:30 PM)\n\n"
                "Try again:"
            )
            return TOB
        
        if minute < 0 or minute > 59:
            await update.message.reply_text(
                "❌ Invalid minute!\n\n"
                "Minutes must be between 00 and 59.\n"
                "⏰ Example: 09:15\n\n"
                "Try again:"
            )
            return TOB
        
        # Format with leading zeros
        tob = f"{hour:02d}:{minute:02d}"
        
    except ValueError:
        await update.message.reply_text(
            "❌ That's not a valid time!\n\n"
            "Please use **HH:MM** format (24-hour).\n"
            "⏰ Example: 14:30 or 09:15\n\n"
            "Try again:"
        )
        return TOB
    
    context.user_data['time_of_birth'] = tob
    
    await update.message.reply_text(
        "Perfect! ✅\n\n"
        "Finally, **where** were you born?\n"
        "📍 Format: City, State/Region or City, Country\n"
        "📝 Example: Hisar, Haryana\n"
        "📝 Example: New Delhi, India\n\n"
        "Be as specific as possible!"
    )
    return POB

async def receive_pob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate place of birth"""
    pob = update.message.text.strip()
    
    # Basic validation
    if len(pob) < 3:
        await update.message.reply_text(
            "❌ That seems too short!\n\n"
            "Please provide your city and state/country.\n"
            "📍 Format: City, State/Region or City, Country\n"
            "📝 Example: Hisar, Haryana\n"
            "📝 Example: New Delhi, India\n\n"
            "Try again:"
        )
        return POB
    
    # Check if it has at least city name
    if ',' not in pob:
        await update.message.reply_text(
            "❌ Please include both city and state/country!\n\n"
            "📍 Format: City, State/Region or City, Country\n"
            "📝 Example: Hisar, Haryana\n"
            "📝 Example: Mumbai, India\n"
            "📝 Example: London, UK\n\n"
            "Try again:"
        )
        return POB
    
    # Check if parts are not empty
    parts = [p.strip() for p in pob.split(',')]
    if any(len(p) < 2 for p in parts):
        await update.message.reply_text(
            "❌ Please provide valid city and state/country names!\n\n"
            "📍 Format: City, State/Region or City, Country\n"
            "📝 Example: Hisar, Haryana\n"
            "📝 Example: Sydney, Australia\n\n"
            "Try again:"
        )
        return POB
    
    context.user_data['place_of_birth'] = pob
    
    # Ask about encryption with keyboard buttons
    keyboard = [['Yes, encrypt my chats 🔐'], ['No, keep them unencrypted']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "Great! ✅\n\n"
        "🔐 **Privacy Option**\n\n"
        "Would you like to **encrypt** your chat messages?\n\n"
        "**Benefits of encryption:**\n"
        "• Your messages are encrypted in our database\n"
        "• Extra layer of privacy protection\n"
        "• Your chats won't appear in logs\n\n"
        "**Note:** This only affects message storage, not functionality.\n\n"
        "Choose an option:",
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
        "Cancelled! 🛑\n\n"
        "You can use /start or /change anytime to set up your details.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Create conversation handler with /start and /change as entry points
birth_details_conversation = ConversationHandler(
    entry_points=[
        CommandHandler('start', start_command),  # Handles /start
        CommandHandler('change', change_command)  # Handles /change
    ],
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