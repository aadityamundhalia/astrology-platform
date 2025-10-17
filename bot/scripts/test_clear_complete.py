"""Test complete clear functionality"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.memory_service import MemoryService

async def test_complete_clear():
    """Test adding and clearing memories"""
    memory_service = MemoryService()
    test_user_id = 999999
    
    print("Testing Complete Clear Flow")
    print("="*60)
    
    # Step 1: Add some test memories
    print("\n1. Adding test memories...")
    for i in range(3):
        result = await memory_service.add_memory(
            user_id=test_user_id,
            user_message=f"Test question {i+1}: What is my favorite color?",
            ai_message=f"Test answer {i+1}: Your favorite color is blue."
        )
        if result:
            print(f"   ✅ Added memory {i+1}")
        else:
            print(f"   ❌ Failed to add memory {i+1}")
    
    # Wait for Mem0 to process
    print("\n   ⏳ Waiting 3 seconds for Mem0 to process...")
    await asyncio.sleep(3)
    
    # Step 2: Get all memories
    print("\n2. Getting all memories...")
    all_memories = await memory_service.get_all_memories(test_user_id)
    count = all_memories.get('count', 0)
    memories = all_memories.get('memories', [])
    print(f"   Total memories: {count}")
    print(f"   Memory type: {type(memories)}")
    
    if memories:
        # Handle both list and dict responses
        if isinstance(memories, list):
            print(f"   Memory details (list):")
            for idx, mem in enumerate(memories[:3], 1):  # Show first 3
                if isinstance(mem, dict):
                    print(f"      {idx}. {mem.get('memory', 'N/A')[:80]}")
                else:
                    print(f"      {idx}. {str(mem)[:80]}")
        elif isinstance(memories, dict):
            print(f"   Memory details (dict):")
            for key, value in list(memories.items())[:3]:
                print(f"      {key}: {str(value)[:80]}")
        else:
            print(f"   Raw memories: {str(memories)[:200]}")
    
    # Step 3: Search for memories
    print("\n3. Searching memories...")
    search_result = await memory_service.get_memories(test_user_id, "favorite color")
    data = search_result.get('data', '')
    print(f"   Search result length: {len(data)} chars")
    if len(data) > 100:
        print(f"   Content preview: {data[:200]}...")
    else:
        print(f"   Content: {data}")
    
    # Step 4: Clear memories (try multiple times if needed)
    print("\n4. Clearing all memories...")
    cleared = await memory_service.clear_memory(test_user_id)
    if cleared:
        print(f"   ✅ Clear operation completed")
    else:
        print(f"   ❌ Clear operation failed")
    
    # Step 5: Final verification
    print("\n5. Final verification...")
    await asyncio.sleep(2)
    all_memories_after = await memory_service.get_all_memories(test_user_id)
    count_after = all_memories_after.get('count', 0)
    memories_after = all_memories_after.get('memories', [])
    
    print(f"   Memories after clear: {count_after}")
    
    if count_after == 0:
        print(f"   ✅ All memories successfully cleared!")
    else:
        print(f"   ⚠️ Still have {count_after} memories remaining")
        if memories_after:
            print(f"   Remaining memories:")
            if isinstance(memories_after, list):
                for idx, mem in enumerate(memories_after, 1):
                    if isinstance(mem, dict):
                        print(f"      {idx}. Memory: {mem.get('memory', 'N/A')[:80]}")
                        print(f"         ID: {mem.get('id', 'N/A')}")
                    else:
                        print(f"      {idx}. {str(mem)[:80]}")
            elif isinstance(memories_after, dict):
                for key, value in memories_after.items():
                    print(f"      {key}: {str(value)[:80]}")
            else:
                print(f"      Raw: {str(memories_after)[:200]}")
    
    print("\n" + "="*60)
    
    return count_after == 0

if __name__ == "__main__":
    success = asyncio.run(test_complete_clear())
    sys.exit(0 if success else 1)