"""RabbitMQ Queue Service with priority support"""
import logging
import json
import asyncio
from aio_pika import connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class QueueService:
    def __init__(self):
        self.connection: AbstractConnection = None
        self.channel: AbstractChannel = None
        self.queue: AbstractQueue = None
        self.is_processing = False
    
    async def connect(self):
        """Connect to RabbitMQ"""
        try:
            logger.info(f"🐰 Connecting to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port}...")
            self.connection = await connect_robust(settings.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            # Set prefetch count based on number of workers
            await self.channel.set_qos(prefetch_count=settings.rabbitmq_workers)
            
            # Declare queue with priority support (max priority 10)
            self.queue = await self.channel.declare_queue(
                settings.rabbitmq_queue,
                durable=True,
                arguments={
                    "x-max-priority": 10  # Enable priority queue (1-10)
                }
            )
            
            logger.info(f"✅ Connected to RabbitMQ - Queue: {settings.rabbitmq_queue} (priority enabled)")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from RabbitMQ"""
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info("🐰 Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    async def publish_request(self, request_data: dict) -> str:
        """Publish a request to the queue with priority"""
        try:
            message_body = json.dumps(request_data).encode()
            
            # Get priority from request (default 5)
            priority = request_data.get('priority', 5)
            # RabbitMQ priority: higher number = higher priority
            # Our system: lower number = higher priority
            # So invert: priority 1 -> RabbitMQ priority 9, priority 10 -> RabbitMQ priority 0
            rabbitmq_priority = 10 - priority
            
            message = Message(
                message_body,
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                priority=rabbitmq_priority  # Set message priority
            )
            
            await self.channel.default_exchange.publish(
                message,
                routing_key=settings.rabbitmq_queue
            )
            
            request_id = request_data.get('request_id', 'unknown')
            logger.info(f"📤 Published request {request_id} (priority: {priority}) to queue")
            
            return request_id
            
        except Exception as e:
            logger.error(f"Error publishing request: {e}")
            raise
    
    async def start_consumer(self, handler):
        """Start consuming messages from the queue"""
        try:
            logger.info(f"🐰 Starting consumer for queue: {settings.rabbitmq_queue}")
            self.is_processing = True
            
            async with self.queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            request_data = json.loads(message.body.decode())
                            request_id = request_data.get('request_id', 'unknown')
                            priority = request_data.get('priority', 5)
                            
                            logger.info(f"📥 Processing request {request_id} (priority: {priority}) from queue")
                            
                            # Call the handler to process the request
                            await handler(request_data)
                            
                            logger.info(f"✅ Completed request {request_id}")
                            
                        except Exception as e:
                            logger.error(f"❌ Error processing message: {e}", exc_info=True)
                            
        except asyncio.CancelledError:
            logger.info("🛑 Consumer stopped")
            self.is_processing = False
        except Exception as e:
            logger.error(f"❌ Consumer error: {e}", exc_info=True)
            self.is_processing = False
    
    async def get_queue_size(self) -> int:
        """Get approximate queue size"""
        try:
            return 0
        except Exception as e:
            logger.error(f"Error getting queue size: {e}")
            return 0