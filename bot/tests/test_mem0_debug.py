import asyncio
import httpx
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import get_settings

settings = get_settings()

async def test_mem0_endpoints():
    """Debug Mem0 API endpoints"""
    base_url = settings.mem0_service_url
    
    print(f"Testing Mem0 at: {base_url}")
    print("=" * 60)
    
    # Test 1: GET /get
    print("\n1. Testing GET /get")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{base_url}/get",
                params={
                    "user_id": "test_user_123",
                    "msg": "test query",
                    "num_chats": 5,
                    "include_chat_history": "false"
                }
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test 2: POST /add with JSON
    print("\n2. Testing POST /add with JSON")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/add",
                json={
                    "user_id": "test_user_123",
                    "user_message": "Hello, how are you?",
                    "ai_message": "I'm doing great!"
                },
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test 3: POST /add with form data
    print("\n3. Testing POST /add with form data")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/add",
                data={
                    "user_id": "test_user_123",
                    "user_message": "Hello, how are you?",
                    "ai_message": "I'm doing great!"
                }
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test 4: Check API docs if available
    print("\n4. Checking for API docs")
    async with httpx.AsyncClient() as client:
        for path in ["/docs", "/redoc", "/openapi.json", "/"]:
            try:
                response = await client.get(f"{base_url}{path}", timeout=5.0)
                if response.status_code == 200:
                    print(f"   ✓ Found docs at: {base_url}{path}")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(test_mem0_endpoints())
