import asyncio
import httpx
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import get_settings

settings = get_settings()

async def test_mem0():
    """Test Mem0 API connection"""
    base_url = settings.mem0_service_url
    
    print(f"Testing Mem0 at: {base_url}")
    print("=" * 60)
    
    # Test 1: Check if service is up
    print("\n1. Testing service availability")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{base_url}/")
            print(f"   ✓ Service is up - Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Service unavailable: {e}")
            return
    
    # Test 2: Add memory
    print("\n2. Testing POST /add")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            payload = {
                "user_id": 123456789,
                "user_message": "Test message",
                "ai_message": "Test response"
            }
            print(f"   Payload: {payload}")
            
            response = await client.post(
                f"{base_url}/add",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                print("   ✓ Add memory successful")
            else:
                print(f"   ✗ Add memory failed")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Test 3: Get memories
    print("\n3. Testing GET /get")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            params = {
                "user_id": 123456789,
                "msg": "test query",
                "num_chats": 5,
                "include_chat_history": "false"
            }
            print(f"   Params: {params}")
            
            response = await client.get(
                f"{base_url}/get",
                params=params
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("   ✓ Get memories successful")
            else:
                print(f"   ✗ Get memories failed")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")

async def main():
    """Main test function"""
    await test_mem0()
    return True  # Basic connectivity test

if __name__ == "__main__":
    asyncio.run(test_mem0())
