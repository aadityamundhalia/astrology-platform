"""Delete RabbitMQ queue"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aio_pika import connect_robust
from config import get_settings

settings = get_settings()

async def delete_queue():
    """Delete the astrology requests queue"""
    try:
        print(f"🐰 Connecting to RabbitMQ...")
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        
        print(f"🗑️ Deleting queue: {settings.rabbitmq_queue}")
        
        # Delete the queue
        await channel.queue_delete(settings.rabbitmq_queue)
        
        print(f"✅ Queue '{settings.rabbitmq_queue}' deleted successfully")
        
        await connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error deleting queue: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(delete_queue())
    sys.exit(0 if success else 1)