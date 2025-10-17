# memory/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

def find_env_file():
    """Find .env file in current or parent directories"""
    current = Path.cwd()
    
    # Check current directory
    env_path = current / '.env'
    if env_path.exists():
        return str(env_path)
    
    # Check parent directories (up to 3 levels)
    for _ in range(3):
        current = current.parent
        env_path = current / '.env'
        if env_path.exists():
            return str(env_path)
    
    # Default to .env in current directory
    return '.env'

# Load environment variables from parent .env if exists
env_file = find_env_file()
load_dotenv(env_file)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "mem0_collection")
OLLAMA_EMBEDDING_BASE_URL = os.getenv("OLLAMA_EMBEDDING_BASE_URL")
USE_LLM_REFORMAT = os.getenv("USE_LLM_REFORMAT", "false").lower() == "true"