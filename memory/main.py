from fastapi import FastAPI
from mem0 import Memory
import json
from pydantic import BaseModel
from config import (
    OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_EMBEDDING_MODEL,
    QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, OLLAMA_EMBEDDING_BASE_URL,
    USE_LLM_REFORMAT
)
import traceback
from typing import Optional
import ollama
import datetime

app = FastAPI()


class AddRequest(BaseModel):
    user_id: int
    user_message: str
    ai_message: str


# CRITICAL FIX: Simplified config without redundant settings
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": QDRANT_COLLECTION,
            "host": QDRANT_HOST,
            "port": QDRANT_PORT,
            "embedding_model_dims": 768,
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": OLLAMA_MODEL,
            "temperature": 0.2,  # Lower temperature for more consistent memory extraction
            "max_tokens": 2000,
            "ollama_base_url": OLLAMA_BASE_URL,
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": OLLAMA_EMBEDDING_MODEL,
            "ollama_base_url": OLLAMA_EMBEDDING_BASE_URL,
        },
    },
    "version": "v1.1"  # CRITICAL: Use v1.1 for better memory operations
}

memory = Memory.from_config(config)


@app.post("/add")
async def add_chat(request: AddRequest):
    user_id = str(request.user_id)
    user_message = request.user_message
    ai_message = request.ai_message

    # CRITICAL FIX: Use proper message format for conversation context
    # Include both user and assistant messages for better context extraction
    message_text = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": ai_message}
    ]

    try:
        # CRITICAL FIX: Single add call with proper parameters
        # The issue was multiple redundant add() calls which can confuse the LLM
        result = memory.add(
            messages=message_text,
            user_id=user_id,
            metadata={
                "timestamp": str(datetime.datetime.utcnow()),
                "type": "conversation"
            }
        )
        
        print(f"Memory add result: {result}")
        
        # Return the actual result for debugging
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        print(f"Error adding to memory: {e}")
        print(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/get")
async def get_memories(
    user_id: str,
    msg: str
):
    # Reformat query using LLM if enabled
    query = msg
    if USE_LLM_REFORMAT:
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{
                    "role": "user",
                    "content": f"Reformat this query to be more suitable for semantic search and memory retrieval. Return only the reformatted query, nothing else: {msg}"
                }]
            )
            query = response['message']['content'].strip()
            print(f"Reformatted query from '{msg}' to '{query}'")
        except Exception as e:
            print(f"Error reformatting query with LLM: {e}")
            # Fall back to original message
    
    # Get memories from Mem0
    try:
        knowledge = memory.search(
            query=query, 
            user_id=user_id, 
            limit=20
        )
        
        print(f"Search results: {knowledge}")
        
        if not knowledge or not knowledge.get("results"):
            return {"data": "<knowledge_about_user>\nNo memories found.\n</knowledge_about_user>"}
        
        knowledge_str = "\n".join(
            f"- {entry['memory']}" for entry in knowledge["results"]
        )

        output = "<knowledge_about_user>\n" + knowledge_str + "\n</knowledge_about_user>"

        return {"data": output}
    except Exception as e:
        print(f"Error retrieving memories: {e}")
        print(traceback.format_exc())
        return {"data": "<knowledge_about_user>\nError retrieving memories.\n</knowledge_about_user>"}


@app.get("/get_all")
async def get_all_memories(user_id: str):
    """
    Get all memories for a user to verify storage
    """
    try:
        all_memories = memory.get_all(user_id=user_id)
        
        # Extract actual memories from results
        if all_memories and isinstance(all_memories, dict):
            results = all_memories.get('results', [])
            return {
                "status": "success",
                "count": len(results),
                "memories": results  # Return the actual list, not the wrapper dict
            }
        elif all_memories and isinstance(all_memories, list):
            return {
                "status": "success",
                "count": len(all_memories),
                "memories": all_memories
            }
        else:
            return {
                "status": "success",
                "count": 0,
                "memories": []
            }
    except Exception as e:
        print(f"Error getting all memories: {e}")
        print(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "count": 0,
            "memories": []
        }


@app.delete("/clear")
async def clear_user_data(user_id: str):
    """
    Clear all memories for a given user
    """
    try:
        print(f"Attempting to delete memories for user {user_id}")
        
        # Get all memories first to delete them individually
        all_memories = memory.get_all(user_id=user_id)
        
        deleted_count = 0
        if all_memories:
            # Handle dict format
            if isinstance(all_memories, dict):
                results = all_memories.get('results', [])
            else:
                results = all_memories if isinstance(all_memories, list) else []
            
            # Delete each memory by ID
            for mem in results:
                try:
                    memory_id = mem.get('id')
                    if memory_id:
                        memory.delete(memory_id=memory_id)
                        deleted_count += 1
                        print(f"Deleted memory {memory_id}")
                except Exception as e:
                    print(f"Error deleting memory {mem.get('id')}: {e}")
        
        # Also call delete_all as backup
        try:
            memory.delete_all(user_id=user_id)
        except Exception as e:
            print(f"delete_all error (non-critical): {e}")
        
        print(f"Successfully deleted {deleted_count} memories for user {user_id}")
        
        return {
            "status": "success",
            "message": f"Cleared {deleted_count} memories for user {user_id}",
            "deleted_count": deleted_count
        }
    except Exception as e:
        print(f"Error clearing data for user {user_id}: {e}")
        print(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Failed to clear data for user {user_id}: {str(e)}"
        }


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "healthy"}