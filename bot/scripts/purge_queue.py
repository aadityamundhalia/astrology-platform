"""Purge all messages from RabbitMQ queue"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aio_pika import connect_robust
from config import get_settings

settings = get_settings()

async def purge_queue():
    """Purge all messages from the astrology requests queue"""
    connection = None
    try:
        print(f"🐰 Connecting to RabbitMQ...")
        connection = await connect_robust(settings.rabbitmq_url, timeout=10.0)
        channel = await connection.channel()
        
        # Declare queue
        queue = await channel.declare_queue(
            settings.rabbitmq_queue,
            durable=True
        )
        
        print(f"🗑️ Purging queue: {settings.rabbitmq_queue}")
        
        # Use queue.purge() method if available, otherwise consume with timeout
        deleted_count = 0
        
        # Try to consume messages with a timeout
        try:
            async with asyncio.timeout(5.0):  # 5 second timeout
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            deleted_count += 1
                            # Decode and show what we're deleting
                            try:
                                data = json.loads(message.body.decode())
                                msg_type = data.get('test', data.get('request_id', 'unknown'))
                                print(f"   Deleted: {msg_type}")
                            except:
                                print(f"   Deleted: [binary message]")
                            
                            # Safety check - stop if we've deleted too many
                            if deleted_count >= 1000:
                                print(f"   ⚠️ Safety limit reached (1000 messages)")
                                break
        except asyncio.TimeoutError:
            print(f"   ⏱️ Timeout reached - no more messages to consume")
        
        print(f"✅ Purged {deleted_count} messages from queue")
        
        if connection and not connection.is_closed:
            await connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error purging queue: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if connection and not connection.is_closed:
            try:
                await connection.close()
            except:
                pass

if __name__ == "__main__":
    success = asyncio.run(purge_queue())
    sys.exit(0 if success else 1)