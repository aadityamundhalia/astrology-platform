"""Test Mem0 clear functionality"""
import asyncio
import httpx
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import get_settings

settings = get_settings()

async def test_mem0_endpoints():
    """Test what endpoints Mem0 service supports"""
    base_url = settings.mem0_service_url
    test_user_id = 999999
    
    print(f"Testing Mem0 at: {base_url}\n")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Add a test memory
        print("\n1. Adding test memory...")
        try:
            response = await client.post(
                f"{base_url}/add",
                json={
                    "user_id": test_user_id,
                    "user_message": "Test message for clearing",
                    "ai_message": "Test response"
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Added test memory")
            else:
                print(f"   ❌ Failed to add memory")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Get memories
        print("\n2. Getting memories...")
        try:
            response = await client.get(
                f"{base_url}/get",
                params={
                    "user_id": test_user_id,
                    "msg": "test",
                    "num_chats": 5
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Retrieved memories")
                print(f"   Response keys: {list(data.keys())}")
            else:
                print(f"   ❌ Failed to get memories")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Try DELETE /delete
        print("\n3. Testing DELETE /delete endpoint...")
        try:
            response = await client.delete(
                f"{base_url}/delete",
                params={"user_id": test_user_id}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
            if response.status_code == 200:
                print(f"   ✅ DELETE /delete works!")
            else:
                print(f"   ⚠️ DELETE /delete returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Try POST /clear
        print("\n4. Testing POST /clear endpoint...")
        try:
            response = await client.post(
                f"{base_url}/clear",
                json={"user_id": test_user_id}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
            if response.status_code == 200:
                print(f"   ✅ POST /clear works!")
            else:
                print(f"   ⚠️ POST /clear returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Try DELETE /clear
        print("\n5. Testing DELETE /clear endpoint...")
        try:
            response = await client.delete(
                f"{base_url}/clear",
                params={"user_id": test_user_id}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
            if response.status_code == 200:
                print(f"   ✅ DELETE /clear works!")
            else:
                print(f"   ⚠️ DELETE /clear returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 6: Try POST /reset
        print("\n6. Testing POST /reset endpoint...")
        try:
            response = await client.post(
                f"{base_url}/reset",
                json={"user_id": test_user_id}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
            if response.status_code == 200:
                print(f"   ✅ POST /reset works!")
            else:
                print(f"   ⚠️ POST /reset returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 7: Check API docs
        print("\n7. Checking for API documentation...")
        for path in ["/docs", "/redoc", "/openapi.json"]:
            try:
                response = await client.get(f"{base_url}{path}", timeout=5.0)
                if response.status_code == 200:
                    print(f"   ✅ Found docs at: {base_url}{path}")
            except:
                pass
    
    print("\n" + "="*60)
    print("\nRecommendation:")
    print("Based on the results above, update MemoryService.clear_memory()")
    print("to use the endpoint that returned status 200")

if __name__ == "__main__":
    asyncio.run(test_mem0_endpoints())