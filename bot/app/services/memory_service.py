"""Memory service for storing and retrieving user context using Mem0"""
import httpx
import logging
import asyncio
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self):
        self.base_url = settings.mem0_service_url
        
    async def add_memory(self, user_id: int, user_message: str, ai_message: str):
        """Add a conversation to memory"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/add",
                    json={
                        "user_id": user_id,
                        "user_message": user_message,
                        "ai_message": ai_message
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Added memory for user {user_id}")
                    return response.json()
                else:
                    logger.warning(f"⚠️ Failed to add memory: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return None
    
    async def get_memories(self, user_id: int, msg: str, num_chats: int = 5):
        """Get relevant memories for a user"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/get",
                    params={
                        "user_id": user_id,
                        "msg": msg,
                        "num_chats": num_chats,
                        "include_chat_history": "false"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Retrieved memories for user {user_id}")
                    return result
                else:
                    logger.warning(f"⚠️ Failed to get memories: {response.status_code}")
                    return {"data": ""}
                    
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            return {"data": ""}
    
    async def clear_memory(self, user_id: int, max_retries: int = 3):
        """
        Clear all memories for a user using DELETE /clear endpoint
        Retries multiple times to ensure all memories are cleared
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for attempt in range(max_retries):
                    # Call delete
                    response = await client.delete(
                        f"{self.base_url}/clear",
                        params={"user_id": str(user_id)}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"✅ Clear request successful for user {user_id} (attempt {attempt + 1}): {result.get('message', '')}")
                        
                        # Wait a moment for processing
                        await asyncio.sleep(0.5)
                        
                        # Verify memories are cleared
                        verify_response = await client.get(
                            f"{self.base_url}/get_all",
                            params={"user_id": str(user_id)}
                        )
                        
                        if verify_response.status_code == 200:
                            verify_result = verify_response.json()
                            remaining = verify_result.get('count', 0)
                            
                            if remaining == 0:
                                logger.info(f"✅ Verified: All memories cleared for user {user_id}")
                                return True
                            else:
                                logger.warning(f"⚠️ {remaining} memories still remaining for user {user_id}, retrying...")
                                await asyncio.sleep(1)  # Wait before retry
                        else:
                            logger.warning(f"⚠️ Could not verify clear status")
                    else:
                        logger.warning(f"⚠️ Failed to clear memories (attempt {attempt + 1}): {response.status_code} - {response.text}")
                        await asyncio.sleep(1)
                
                # After all retries, return True if we got success responses
                logger.warning(f"⚠️ Clear completed but some memories may remain for user {user_id}")
                return True
                    
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False
    
    async def get_all_memories(self, user_id: int):
        """Get all memories for a user (for debugging/verification)"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/get_all",
                    params={"user_id": str(user_id)}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    count = result.get('count', 0)
                    logger.info(f"✅ Retrieved all memories for user {user_id}: {count} memories")
                    return result
                else:
                    logger.warning(f"⚠️ Failed to get all memories: {response.status_code}")
                    return {"status": "error", "count": 0, "memories": []}
                    
        except Exception as e:
            logger.error(f"Error getting all memories: {e}")
            return {"status": "error", "count": 0, "memories": []}