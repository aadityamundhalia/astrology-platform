"""Main application entry point"""
import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
import httpx

from config import get_settings
from app.services.telegram_service import TelegramService
from app.services.memory_service import MemoryService
from app.services.astrology_service import AstrologyService
from app.services.queue_service import QueueService
from app.agents.rudie_agent import RudieAgent
from app.agents.extraction_agent import ExtractionAgent
from app.workers.astrology_worker import AstrologyWorker
from app.agents.warning_agent import WarningAgent

from app.handlers.command_handlers import (
    handle_help,
    handle_clear,
    handle_info
)
from app.handlers.conversation_handlers import birth_details_conversation
from app.handlers.message_handler import handle_message

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
telegram_service = TelegramService()
memory_service = MemoryService()
astrology_service = AstrologyService()
queue_service = QueueService()

# Initialize agents
extraction_agent = ExtractionAgent()
rudie_agent = RudieAgent(astrology_service)
warning_agent = WarningAgent()

# Initialize worker
astrology_worker = AstrologyWorker(
    telegram_service=telegram_service,
    memory_service=memory_service,
    astrology_service=astrology_service,
    rudie_agent=rudie_agent
)

# Create FastAPI app
app = FastAPI(title="Astrology Bot")

# Wrapper functions for handlers - REMOVE _handle_start
# async def _handle_start(update, context):
#     """Wrapper for start handler"""
#     return await handle_start(update, context, telegram_service)

async def _handle_help(update, context):
    """Wrapper for help handler"""
    return await handle_help(update, context)

async def _handle_info(update, context):
    """Wrapper for info handler"""
    return await handle_info(update, context)

async def _handle_clear(update, context):
    """Wrapper for clear handler"""
    return await handle_clear(update, context, telegram_service, memory_service)

async def _handle_message(update, context):
    """Wrapper for message handler"""
    return await handle_message(
        update,
        context,
        telegram_service,
        queue_service,
        extraction_agent
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting astrology bot...")
    
    # Test Mem0 connection
    try:
        logger.info("🧠 Testing Mem0 connection...")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.mem0_service_url}/health")
            logger.info(f"🧠 Mem0 service responding: HTTP {response.status_code}")
            if response.status_code == 200:
                logger.info(f"✅ Mem0 service is healthy")
            else:
                logger.warning(f"⚠️  Mem0 service returned non-200 status")
    except Exception as e:
        logger.warning(f"🧠 Could not connect to Mem0 service: {e}")
        logger.warning("⚠️  Bot will continue but memory features may not work")
    
    # Test encryption
    try:
        from app.utils.encryption import get_encryption
        encryption = get_encryption()
        test_encrypted = encryption.encrypt("test")
        test_decrypted = encryption.decrypt(test_encrypted)
        if test_decrypted == "test":
            logger.info("🔐 Encryption system initialized successfully")
        else:
            logger.error("❌ Encryption test failed")
    except Exception as e:
        logger.error(f"❌ Encryption initialization failed: {e}")
        logger.error("⚠️  Chat encryption will not work!")
    
    # Connect to RabbitMQ
    try:
        await queue_service.connect()
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
        raise
    
    # Start multiple consumers based on RABBITMQ_WORKERS
    consumer_tasks = []
    for worker_id in range(settings.rabbitmq_workers):
        logger.info(f"👷 Starting worker {worker_id + 1}/{settings.rabbitmq_workers}")
        task = asyncio.create_task(
            queue_service.start_consumer(astrology_worker.process_request),
            name=f"worker-{worker_id}"
        )
        consumer_tasks.append(task)
    
    logger.info(f"✅ Started {settings.rabbitmq_workers} worker(s)")
    
    # Start Telegram bot - REMOVE start_handler parameter
    application = telegram_service.setup_application(
        message_handler=_handle_message,
        conversation_handler=birth_details_conversation,
        clear_handler=_handle_clear,
        help_handler=_handle_help,
        info_handler=_handle_info
        # start_handler=_handle_start,  # REMOVE THIS LINE
    )
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("✅ Telegram bot started successfully")
    
    # Yield control to FastAPI (app is now running)
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down astrology bot...")
    
    # Stop all consumers
    for task in consumer_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    logger.info("✅ All workers stopped")
    
    # Disconnect from RabbitMQ
    await queue_service.disconnect()
    
    # Stop Telegram bot
    if telegram_service.application:
        await telegram_service.application.updater.stop()
        await telegram_service.application.stop()
        await telegram_service.application.shutdown()
    logger.info("✅ Telegram bot stopped")

# Use lifespan
app = FastAPI(title="Astrology Bot", lifespan=lifespan)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Astrology Bot is running", "bot": "rudie"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot": "rudie",
        "version": "1.0.0",
        "encryption": "enabled"
    }

@app.get("/queue/status")
async def queue_status():
    """Get queue status"""
    return {
        "is_processing": queue_service.is_processing,
        "queue_ready": queue_service.queue is not None,
        "workers": settings.rabbitmq_workers
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8282)