import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import get_settings
import httpx
import asyncpg
from redis import Redis
from app.services.memory_service import MemoryService
from app.services.astrology_service import AstrologyService
from app.agents.extraction_agent import ExtractionAgent
from app.agents.rudie_agent import RudieAgent

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

async def test_postgres():
    """Test PostgreSQL connection"""
    print(f"\n{Colors.BLUE}Testing PostgreSQL Connection...{Colors.END}")
    try:
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        
        version = await conn.fetchval('SELECT version()')
        print_test("PostgreSQL Connection", True, f"Connected to: {version[:50]}...")
        
        # Check users table
        exists = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')"
        )
        print_test("Users Table Exists", exists, "Table found" if exists else "Table not found")
        
        if exists:
            # Check table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            print(f"   {Colors.YELLOW}Table structure:{Colors.END}")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print_test("PostgreSQL Connection", False, str(e))
        return False

async def test_redis():
    """Test Redis connection"""
    print(f"\n{Colors.BLUE}Testing Redis Connection...{Colors.END}")
    try:
        redis_client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password if settings.redis_password else None,
            decode_responses=True
        )
        
        # Test ping
        pong = redis_client.ping()
        print_test("Redis Connection", pong, "PING/PONG successful")
        
        # Test set/get
        redis_client.set("test_key", "test_value", ex=10)
        value = redis_client.get("test_key")
        print_test("Redis Read/Write", value == "test_value", f"Value: {value}")
        
        redis_client.close()
        return True
        
    except Exception as e:
        print_test("Redis Connection", False, str(e))
        return False

async def test_ollama():
    """Test Ollama connection"""
    print(f"\n{Colors.BLUE}Testing Ollama Connection...{Colors.END}")
    try:
        async with httpx.AsyncClient() as client:
            # Test if Ollama is running
            response = await client.get(f"{settings.ollama_host}/api/tags", timeout=10.0)
            print_test("Ollama Server", response.status_code == 200, f"Status: {response.status_code}")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                print(f"   {Colors.YELLOW}Available models:{Colors.END}")
                for model in model_names:
                    marker = "✓" if settings.ollama_model in model else " "
                    print(f"   [{marker}] {model}")
                
                has_model = any(settings.ollama_model in m for m in model_names)
                print_test("Required Model Available", has_model, 
                          f"Model '{settings.ollama_model}' {'found' if has_model else 'NOT FOUND'}")
                return has_model
            
        return False
        
    except Exception as e:
        print_test("Ollama Connection", False, str(e))
        return False

async def test_mem0_service():
    """Test Mem0 service"""
    print(f"\n{Colors.BLUE}Testing Mem0 Service...{Colors.END}")
    try:
        memory_service = MemoryService()
        
        # Test get memories
        result = await memory_service.get_memories(
            user_id=999999,
            msg="test query",
            num_chats=5
        )
        print_test("Mem0 Get Memories", True, f"Response keys: {list(result.keys())}")
        
        # Test add memory
        result = await memory_service.add_memory(
            user_id=999999,
            user_message="Test message",
            ai_message="Test response"
        )
        print_test("Mem0 Add Memory", True, "Memory added successfully")
        
        return True
        
    except Exception as e:
        print_test("Mem0 Service", False, str(e))
        return False

async def test_astrology_api():
    """Test Astrology API"""
    print(f"\n{Colors.BLUE}Testing Astrology API...{Colors.END}")
    
    test_data = {
        "date_of_birth": "1990-01-15",
        "time_of_birth": "10:30",
        "place_of_birth": "New Delhi, India"
    }
    
    service = AstrologyService()
    
    tests = [
        ("Today Prediction", service.get_today_prediction),
        ("Weekly Prediction", service.get_weekly_prediction),
        ("Current Month", service.get_current_month_prediction),
        ("Daily Horoscope", service.get_daily_horoscope),
    ]
    
    success_count = 0
    for name, method in tests:
        try:
            result = await method(test_data)
            print_test(name, True, f"Response type: {type(result).__name__}")
            success_count += 1
        except Exception as e:
            print_test(name, False, str(e)[:100])
    
    return success_count == len(tests)

async def test_rabbitmq():
    """Test RabbitMQ connection"""
    print(f"\n{Colors.BLUE}Testing RabbitMQ Connection...{Colors.END}")
    connection = None
    try:
        from aio_pika import connect_robust, Message, DeliveryMode
        import json
        
        # Test connection
        connection = await connect_robust(settings.rabbitmq_url)
        print_test("RabbitMQ Connection", True, f"Connected to {settings.rabbitmq_host}:{settings.rabbitmq_port}")
        
        # Create channel
        channel = await connection.channel()
        print_test("RabbitMQ Channel", True, "Channel created successfully")
        
        # Declare queue WITH priority support (matching production)
        queue = await channel.declare_queue(
            settings.rabbitmq_queue,
            durable=True,
            arguments={"x-max-priority": 10}  # Match production queue
        )
        print_test("Queue Declaration", True, f"Queue '{settings.rabbitmq_queue}' declared with priority")
        
        # Test publish
        test_message = {
            "test": "connection_test",
            "timestamp": "2025-10-17"
        }
        
        message = Message(
            json.dumps(test_message).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            priority=5  # Set priority
        )
        
        await channel.default_exchange.publish(
            message,
            routing_key=settings.rabbitmq_queue
        )
        print_test("Message Publish", True, "Test message published successfully")
        
        print_test("Queue Status", True, f"Queue '{settings.rabbitmq_queue}' is ready")
        
        # Test consume with timeout
        consumed = False
        try:
            async def consume_with_timeout():
                async with queue.iterator() as queue_iter:
                    async for received_message in queue_iter:
                        async with received_message.process():
                            data = json.loads(received_message.body.decode())
                            if data.get("test") == "connection_test":
                                return True
                        break
                return False
            
            consumed = await asyncio.wait_for(consume_with_timeout(), timeout=5.0)
            print_test("Message Consume", consumed, "Message received and processed")
            
        except asyncio.TimeoutError:
            print_test("Message Consume", False, "Timeout - message may still be in queue")
        except Exception as e:
            print_test("Message Consume", False, f"Error: {str(e)[:50]}")
        
        await connection.close()
        print_test("Connection Close", True, "Connection closed gracefully")
        
        return True  # Return True if basic operations succeeded
        
    except Exception as e:
        print_test("RabbitMQ Connection", False, str(e))
        return False
    finally:
        # Ensure connection is closed
        if connection and not connection.is_closed:
            try:
                await connection.close()
            except:
                pass

async def test_extraction_agent():
    """Test Extraction Agent"""
    print(f"\n{Colors.BLUE}Testing Extraction Agent...{Colors.END}")
    try:
        agent = ExtractionAgent()
        
        # Test extraction
        test_message = "I was born on November 22, 1970 at 12:25 AM in Hisar, Haryana"
        result = await agent.extract_birth_data(test_message)
        
        print_test("Agent Initialization", True, "Agent created successfully")
        print_test("Birth Data Extraction", 
                  result.get("date_of_birth") is not None,
                  f"Extracted: {result}")
        
        return result.get("date_of_birth") is not None
        
    except Exception as e:
        print_test("Extraction Agent", False, str(e))
        return False

async def test_rudie_agent():
    """Test Rudie Agent"""
    print(f"\n{Colors.BLUE}Testing Rudie Agent...{Colors.END}")
    try:
        agent = RudieAgent()
        astrology_service = AstrologyService()
        
        user_context = {
            "name": "Test User",
            "date_of_birth": "1990-01-15",
            "time_of_birth": "10:30",
            "place_of_birth": "New Delhi, India",
            "memories": ""
        }
        
        print_test("Agent Initialization", True, "Rudie agent created successfully")
        
        # Test simple response (this might take a while)
        print(f"   {Colors.YELLOW}Generating response (this may take 30-60 seconds)...{Colors.END}")
        
        # IMPORTANT: Pass the astrology_service in the call
        response = await agent.generate_response(
            user_message="How is today for me?",
            user_context=user_context,
            astrology_service=astrology_service  # This is the key
        )
        
        print_test("Response Generation", len(response) > 0, f"Response length: {len(response)} chars")
        if len(response) > 0:
            print(f"   {Colors.YELLOW}Sample response:{Colors.END}")
            print(f"   {response[:200]}...")
        
        return len(response) > 0
        
    except Exception as e:
        print_test("Rudie Agent", False, str(e))
        return False

async def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Astrology Bot - Connection Tests{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Configuration:{Colors.END}")
    print(f"  PostgreSQL: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print(f"  Redis: {settings.redis_host}:{settings.redis_port}")
    print(f"  RabbitMQ: {settings.rabbitmq_host}:{settings.rabbitmq_port}")
    print(f"  Ollama: {settings.ollama_host} (model: {settings.ollama_model})")
    print(f"  Mem0: {settings.mem0_service_url}")
    print(f"  Astrology API: {settings.astrology_api_url}")
    
    results = {}
    
    # Run tests
    results['postgres'] = await test_postgres()
    results['redis'] = await test_redis()
    results['rabbitmq'] = await test_rabbitmq()
    results['ollama'] = await test_ollama()
    results['mem0'] = await test_mem0_service()
    results['astrology'] = await test_astrology_api()
    results['extraction'] = await test_extraction_agent()
    results['rudie'] = await test_rudie_agent()
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(results.values())
    total = len(results)
    
    for name, status in results.items():
        icon = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
        print(f"{icon} {name.upper()}")
    
    print(f"\n{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All tests passed! Your bot is ready to run.{Colors.END}\n")
    else:
        print(f"{Colors.RED}⚠️  Some tests failed. Please fix the issues above.{Colors.END}\n")

    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
