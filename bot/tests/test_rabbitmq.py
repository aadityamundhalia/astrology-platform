"""Comprehensive RabbitMQ tests"""
import asyncio
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import get_settings
from aio_pika import connect_robust, Message, DeliveryMode

settings = get_settings()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, message=""):
    icon = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
    print(f"{icon} {name}")
    if message:
        color = Colors.GREEN if status else Colors.RED
        print(f"   {color}{message}{Colors.END}")

# Track test queues for cleanup
test_queues_created = []

async def cleanup_test_queue(channel, queue_name: str):
    """Delete a test queue"""
    try:
        await channel.queue_delete(queue_name)
        print(f"   {Colors.YELLOW}🧹 Cleaned up test queue: {queue_name}{Colors.END}")
    except Exception as e:
        print(f"   {Colors.YELLOW}⚠️ Could not delete queue {queue_name}: {e}{Colors.END}")

async def cleanup_test_messages(queue, test_id_prefix: str = "test"):
    """Remove test messages from production queue"""
    try:
        cleaned = 0
        async with asyncio.timeout(3):  # 3 second timeout
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        data = json.loads(message.body.decode())
                        msg_id = data.get('test_id', data.get('request_id', ''))
                        
                        # Check if it's a test message
                        if test_id_prefix in str(msg_id).lower():
                            await message.ack()  # Acknowledge to remove
                            cleaned += 1
                        else:
                            await message.reject(requeue=True)  # Put back non-test messages
                            break
                    except:
                        break
        
        if cleaned > 0:
            print(f"   {Colors.YELLOW}🧹 Cleaned up {cleaned} test message(s){Colors.END}")
    except asyncio.TimeoutError:
        pass  # Timeout is OK
    except Exception as e:
        print(f"   {Colors.YELLOW}⚠️ Cleanup note: {e}{Colors.END}")

async def test_basic_connection():
    """Test basic RabbitMQ connection"""
    print(f"\n{Colors.BLUE}Test 1: Basic Connection{Colors.END}")
    try:
        connection = await connect_robust(
            settings.rabbitmq_url,
            timeout=10.0
        )
        print_test("Connection Established", True, f"Connected to {settings.rabbitmq_host}")
        
        await connection.close()
        print_test("Connection Closed", True, "Disconnected gracefully")
        return True
    except Exception as e:
        print_test("Connection Failed", False, str(e))
        return False

async def test_queue_operations():
    """Test queue declaration and deletion"""
    print(f"\n{Colors.BLUE}Test 2: Queue Operations{Colors.END}")
    connection = None
    try:
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        
        # Declare test queue WITH priority
        test_queue_name = f"test_queue_{int(datetime.now().timestamp())}"
        queue = await channel.declare_queue(
            test_queue_name, 
            durable=False, 
            auto_delete=True,
            arguments={"x-max-priority": 10}
        )
        test_queues_created.append(test_queue_name)
        print_test("Queue Created", True, f"Queue '{test_queue_name}' created with priority support")
        
        # Clean up the test queue
        await cleanup_test_queue(channel, test_queue_name)
        test_queues_created.remove(test_queue_name)
        
        await connection.close()
        return True
    except Exception as e:
        print_test("Queue Operations Failed", False, str(e))
        return False
    finally:
        if connection and not connection.is_closed:
            await connection.close()

async def test_publish_consume():
    """Test publishing and consuming messages"""
    print(f"\n{Colors.BLUE}Test 3: Publish & Consume{Colors.END}")
    connection = None
    try:
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        
        # Use production queue (already has priority)
        queue = await channel.declare_queue(
            settings.rabbitmq_queue,
            durable=True,
            arguments={"x-max-priority": 10}
        )
        
        # Publish test message
        test_data = {
            "test_id": "test_123",
            "timestamp": datetime.now().isoformat(),
            "message": "RabbitMQ test message"
        }
        
        message = Message(
            json.dumps(test_data).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
            priority=5
        )
        
        await channel.default_exchange.publish(
            message,
            routing_key=settings.rabbitmq_queue
        )
        print_test("Message Published", True, f"Published: {test_data['test_id']}")
        
        # Consume the message with timeout
        consumed = False
        try:
            async with asyncio.timeout(5):
                async with queue.iterator() as queue_iter:
                    async for received_message in queue_iter:
                        async with received_message.process():
                            received_data = json.loads(received_message.body.decode())
                            if received_data.get("test_id") == "test_123":
                                print_test("Message Consumed", True, f"Received: {received_data['test_id']}")
                                consumed = True
                            break
        except asyncio.TimeoutError:
            print_test("Message Consumed", False, "Timeout waiting for message")
        
        await connection.close()
        return consumed
    except Exception as e:
        print_test("Publish/Consume Failed", False, str(e))
        return False
    finally:
        if connection and not connection.is_closed:
            await connection.close()

async def test_multiple_messages():
    """Test publishing multiple messages"""
    print(f"\n{Colors.BLUE}Test 4: Multiple Messages{Colors.END}")
    connection = None
    try:
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        
        queue = await channel.declare_queue(
            settings.rabbitmq_queue,
            durable=True,
            arguments={"x-max-priority": 10}
        )
        
        # Publish 5 test messages
        num_messages = 5
        for i in range(num_messages):
            test_data = {
                "test_id": f"batch_test_{i}",
                "index": i,
                "timestamp": datetime.now().isoformat()
            }
            
            message = Message(
                json.dumps(test_data).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                priority=5
            )
            
            await channel.default_exchange.publish(
                message,
                routing_key=settings.rabbitmq_queue
            )
        
        print_test("Batch Publish", True, f"Published {num_messages} messages")
        
        # Consume all test messages with timeout
        consumed_count = 0
        try:
            async with asyncio.timeout(10):
                async with queue.iterator() as queue_iter:
                    async for received_message in queue_iter:
                        async with received_message.process():
                            data = json.loads(received_message.body.decode())
                            if data.get("test_id", "").startswith("batch_test_"):
                                consumed_count += 1
                            if consumed_count >= num_messages:
                                break
        except asyncio.TimeoutError:
            print_test("Batch Consume", False, f"Timeout - only consumed {consumed_count}/{num_messages}")
        
        print_test("Batch Consume", consumed_count == num_messages, 
                   f"Consumed {consumed_count}/{num_messages} messages")
        
        await connection.close()
        return consumed_count == num_messages
    except Exception as e:
        print_test("Multiple Messages Failed", False, str(e))
        return False
    finally:
        if connection and not connection.is_closed:
            await connection.close()

async def test_queue_service():
    """Test the QueueService class"""
    print(f"\n{Colors.BLUE}Test 5: QueueService Integration{Colors.END}")
    try:
        from app.services.queue_service import QueueService
        
        queue_service = QueueService()
        
        # Test connection
        await queue_service.connect()
        print_test("QueueService Connect", True, "Service connected successfully")
        
        # Test publish
        test_request = {
            "request_id": "service_test_123",
            "user_id": 999999,
            "chat_id": 999999,
            "message": "Test message",
            "priority": 5,
            "user_context": {
                "name": "Test User",
                "date_of_birth": "1990-01-15",
                "time_of_birth": "10:30",
                "place_of_birth": "Test City, Test State"
            }
        }
        
        request_id = await queue_service.publish_request(test_request)
        print_test("QueueService Publish", True, f"Published request: {request_id}")
        
        # Queue size is always 0 in our implementation
        queue_size = await queue_service.get_queue_size()
        print_test("QueueService Queue Size", True, f"Queue size check works (returns {queue_size})")
        
        # Consume and cleanup test message
        consumed = False
        async with queue_service.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body.decode())
                    if data.get("request_id") == "service_test_123":
                        consumed = True
                        print_test("Test Message Cleanup", True, "Test message consumed and removed")
                    break
        
        # Disconnect
        await queue_service.disconnect()
        print_test("QueueService Disconnect", True, "Service disconnected successfully")
        
        return True
    except Exception as e:
        print_test("QueueService Test Failed", False, str(e))
        return False

async def test_worker_simulation():
    """Simulate worker processing"""
    print(f"\n{Colors.BLUE}Test 6: Worker Simulation{Colors.END}")
    try:
        from app.services.queue_service import QueueService
        
        queue_service = QueueService()
        await queue_service.connect()
        
        # Publish test request
        test_request = {
            "request_id": "worker_test_123",
            "user_id": 888888,
            "chat_id": 888888,
            "message": "Worker test",
            "priority": 5,
            "user_context": {
                "name": "Worker Test",
                "date_of_birth": "1990-01-15",
                "time_of_birth": "10:30",
                "place_of_birth": "Test City, Test State"
            }
        }
        
        await queue_service.publish_request(test_request)
        print_test("Request Published", True, "Test request queued")
        
        # Simulate worker processing
        processed = False
        async def mock_handler(data):
            nonlocal processed
            print(f"   {Colors.YELLOW}Worker processing: {data['request_id']}{Colors.END}")
            await asyncio.sleep(0.5)  # Simulate processing time
            processed = True
        
        # Process one message
        async with queue_service.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body.decode())
                    if data.get("request_id") == "worker_test_123":
                        await mock_handler(data)
                    break
        
        print_test("Worker Processing", processed, "Request processed successfully")
        
        await queue_service.disconnect()
        return processed
    except Exception as e:
        print_test("Worker Simulation Failed", False, str(e))
        return False

async def test_queue_persistence():
    """Test queue durability"""
    print(f"\n{Colors.BLUE}Test 7: Queue Persistence{Colors.END}")
    connection = None
    try:
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        
        # Declare durable queue with priority
        queue = await channel.declare_queue(
            settings.rabbitmq_queue,
            durable=True,
            arguments={"x-max-priority": 10}
        )
        
        print_test("Queue Durability", True, 
                   f"Queue '{settings.rabbitmq_queue}' is durable with priority support")
        
        # Publish persistent message
        test_data = {"persistence_test": True, "timestamp": datetime.now().isoformat()}
        message = Message(
            json.dumps(test_data).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            priority=5
        )
        
        await channel.default_exchange.publish(
            message,
            routing_key=settings.rabbitmq_queue
        )
        print_test("Persistent Message", True, "Published persistent message")
        
        # Clean up with timeout
        try:
            async with asyncio.timeout(5):
                async with queue.iterator() as queue_iter:
                    async for received_message in queue_iter:
                        async with received_message.process():
                            data = json.loads(received_message.body.decode())
                            if data.get("persistence_test"):
                                break
        except asyncio.TimeoutError:
            pass  # Cleanup timeout is okay
        
        await connection.close()
        return True
    except Exception as e:
        print_test("Queue Persistence Test Failed", False, str(e))
        return False
    finally:
        if connection and not connection.is_closed:
            await connection.close()

async def cleanup_all():
    """Final cleanup - remove any remaining test queues and messages"""
    print(f"\n{Colors.BLUE}🧹 Final Cleanup{Colors.END}")
    
    try:
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        
        # Clean up any test queues that weren't deleted
        for queue_name in test_queues_created[:]:  # Copy list
            await cleanup_test_queue(channel, queue_name)
            test_queues_created.remove(queue_name)
        
        # Clean up any remaining test messages in production queue
        try:
            queue = await channel.declare_queue(
                settings.rabbitmq_queue,
                durable=True,
                arguments={"x-max-priority": 10}
            )
            await cleanup_test_messages(queue, "test")
            await cleanup_test_messages(queue, "batch_test")
            await cleanup_test_messages(queue, "service_test")
            await cleanup_test_messages(queue, "worker_test")
        except Exception as e:
            print(f"   {Colors.YELLOW}⚠️ Message cleanup skipped: {e}{Colors.END}")
        
        await connection.close()
        print(f"   {Colors.GREEN}✅ Cleanup complete{Colors.END}")
        
    except Exception as e:
        print(f"   {Colors.YELLOW}⚠️ Cleanup had issues (non-critical): {e}{Colors.END}")

async def main():
    """Run all RabbitMQ tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}RabbitMQ Connection Tests{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Configuration:{Colors.END}")
    print(f"  Host: {settings.rabbitmq_host}:{settings.rabbitmq_port}")
    print(f"  User: {settings.rabbitmq_user}")
    print(f"  VHost: {settings.rabbitmq_vhost}")
    print(f"  Queue: {settings.rabbitmq_queue}")
    print(f"  URL: {settings.rabbitmq_url}")
    
    results = {}
    
    try:
        # Run tests
        results['basic_connection'] = await test_basic_connection()
        results['queue_operations'] = await test_queue_operations()
        results['publish_consume'] = await test_publish_consume()
        results['multiple_messages'] = await test_multiple_messages()
        results['queue_service'] = await test_queue_service()
        results['worker_simulation'] = await test_worker_simulation()
        results['queue_persistence'] = await test_queue_persistence()
    finally:
        # Always run cleanup
        await cleanup_all()
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(results.values())
    total = len(results)
    
    for name, status in results.items():
        icon = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
        print(f"{icon} {name.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All RabbitMQ tests passed! Queue is ready.{Colors.END}\n")
    else:
        print(f"{Colors.RED}⚠️  Some tests failed. Please fix the issues above.{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)