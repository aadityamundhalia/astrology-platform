# Mem0 Chat Memory API

A FastAPI-based chat memory system that leverages Mem0 for persistent, user-specific conversation memory. Store and retrieve contextual knowledge across sessions using vector embeddings in Qdrant.

## Features

- **Intelligent Memory Management**: Use Mem0 for persistent, user-specific memory storage and retrieval
- **Vector Search**: Qdrant-powered semantic search for relevant memories
- **LLM Integration**: Ollama-based embeddings and language models
- **RESTful API**: Simple endpoints for adding conversations and retrieving memories
- **Docker Support**: Easy containerized deployment

## Prerequisites

### For Local Development
- Python 3.11+
- Qdrant vector database
- Ollama with required models

### For Docker Deployment
- Docker and Docker Compose
- External services (Qdrant, Ollama) or use included Docker setup

## Installation

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aadityamundhalia/astrology-mem0.git
   cd mem0
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file or set environment variables:
   ```bash
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   OLLAMA_EMBEDDING_MODEL=nomic-embed-text
   OLLAMA_EMBEDDING_BASE_URL=http://localhost:11434
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   QDRANT_COLLECTION=mem0_collection
   USE_LLM_REFORMAT=false  # Set to true to enable LLM-based query reformatting
   ```

5. **Start external services**:
   - Qdrant
   - Ollama (with models `llama3.2` and `nomic-embed-text`)

6. **Start the application**:
   ```bash
   uvicorn main:app --reload
   ```

### Docker Deployment

1. **Ensure external services are running** (Qdrant, Ollama)

2. **Build and start**:
   ```bash
   docker-compose up --build -d
   ```

## API Documentation

### POST /add
Add a new conversation to memory. Both user and AI messages are stored for better context extraction.

**Request Body**:
```json
{
  "user_id": 123456789,
  "user_message": "What movie should I watch?",
  "ai_message": "I recommend Inception!"
}
```

**Notes**:
- Both user and AI messages are stored in Mem0 memory for comprehensive context retrieval
- Memory extraction is configured for optimal storage
- Returns the memory addition result for debugging

**Response**:
```json
{
  "status": "success",
  "result": {
    "id": "mem_123",
    "event": "ADD",
    "data": "..."
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "error": "Memory error details"
}
```

### GET /get
Retrieve relevant memories for a user based on a query.

**Query Parameters**:
- `user_id` (required): User identifier
- `msg` (required): Query message for finding relevant memories

**Notes**:
- If `USE_LLM_REFORMAT=true`, the `msg` parameter will be reformatted using the LLM for better search results before querying memories.
- Returns up to 20 relevant memories for the user
- If no memories are found, returns "No memories found."

**Response**:
```json
{
  "data": "<knowledge_about_user>\n- User prefers action movies\n- User likes sci-fi genre\n</knowledge_about_user>"
}
```

**No Memories Response**:
```json
{
  "data": "<knowledge_about_user>\nNo memories found.\n</knowledge_about_user>"
}
```

**Error Response**:
```json
{
  "data": "<knowledge_about_user>\nError retrieving memories.\n</knowledge_about_user>"
}
```

### GET /get_all
Retrieve all memories for a user for verification purposes.

**Query Parameters**:
- `user_id` (required): User identifier

**Response**:
```json
{
  "status": "success",
  "count": 2,
  "memories": [
    {
      "id": "mem_123",
      "memory": "User likes action movies",
      "metadata": {...}
    },
    {
      "id": "mem_124",
      "memory": "User prefers sci-fi genre",
      "metadata": {...}
    }
  ]
}
```

**Error Response**:
```json
{
  "status": "error",
  "error": "Error details"
}
```

### DELETE /clear
Clear all memories for a specific user.

**Query Parameters**:
- `user_id` (required): User identifier to clear data for

**Response**:
```json
{
  "status": "success",
  "message": "Cleared all memories for user Y"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Failed to clear data for user Y: error details"
}
```

### GET /health
Check the health status of the service.

**Response**:
```json
{
  "status": "healthy"
}
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Development

### Code Structure
- `main.py`: FastAPI application and endpoints
- `config.py`: Configuration settings
- `tests/`: Unit tests

### Adding New Features
1. Update API endpoints in `main.py`
2. Add tests in `tests/`
3. Update documentation

### Rebuilding Docker
After code changes:
```bash
docker-compose build
docker-compose up -d
```

## Logs

Check application logs:
```bash
# Local
# Logs appear in terminal when running uvicorn

# Docker
docker-compose logs -f app
```

## Stopping

```bash
# Local
# Ctrl+C to stop uvicorn

# Docker
docker-compose down
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT