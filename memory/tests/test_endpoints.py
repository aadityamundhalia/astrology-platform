import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch('main.memory')
def test_add_chat_success(mock_memory):
    mock_result = {"id": "mem123"}
    mock_memory.add = MagicMock(return_value=mock_result)
    
    response = client.post("/add", json={
        "user_id": 1,
        "user_message": "Hello",
        "ai_message": "Hi there"
    })
    
    assert response.status_code == 200
    assert response.json() == {"status": "success", "result": mock_result}

@patch('main.memory')
def test_add_chat_memory_error(mock_memory):
    mock_memory.add = MagicMock(side_effect=Exception("Memory error"))
    
    response = client.post("/add", json={
        "user_id": 1,
        "user_message": "Hello",
        "ai_message": "Hi there"
    })
    
    assert response.status_code == 200
    assert response.json() == {"status": "error", "error": "Memory error"}

@patch('main.memory')
@patch('main.ollama.chat')
def test_get_memories_with_reformat(mock_ollama_chat, mock_memory):
    # Mock USE_LLM_REFORMAT to True, but since it's imported, patch it
    with patch('main.USE_LLM_REFORMAT', True):
        mock_ollama_chat.return_value = {'message': {'content': 'Reformatted query'}}
        mock_memory.search.return_value = {"results": [{"memory": "Test memory"}]}
        
        response = client.get("/get?user_id=1&msg=Hello")
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "<knowledge_about_user>" in data
        assert "Test memory" in data

@patch('main.memory')
@patch('main.ollama.chat')
def test_get_memories_without_reformat(mock_ollama_chat, mock_memory):
    with patch('main.USE_LLM_REFORMAT', False):
        mock_memory.search.return_value = {"results": [{"memory": "Test memory"}]}
        
        response = client.get("/get?user_id=1&msg=Hello")
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "<knowledge_about_user>" in data
        assert "Test memory" in data
        mock_ollama_chat.assert_not_called()

@patch('main.memory')
def test_get_memories_error(mock_memory):
    mock_memory.search.side_effect = Exception("Search error")
    
    response = client.get("/get?user_id=1&msg=Hello")
    
    assert response.status_code == 200
    assert response.json()["data"] == "<knowledge_about_user>\nError retrieving memories.\n</knowledge_about_user>"

@patch('main.memory')
def test_clear_memories_success(mock_memory):
    mock_memory.delete_all = MagicMock()
    
    response = client.delete("/clear?user_id=1")
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_memory.delete_all.assert_called_with(user_id="1")

@patch('main.memory')
def test_clear_memories_error(mock_memory):
    mock_memory.delete_all = MagicMock(side_effect=Exception("Delete error"))
    
    response = client.delete("/clear?user_id=1")
    
    assert response.status_code == 200
    assert response.json()["status"] == "error"

def test_health_check():
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('main.memory')
def test_get_all_memories_success(mock_memory):
    mock_memories = [{"id": "mem1", "memory": "Test memory"}]
    mock_memory.get_all = MagicMock(return_value=mock_memories)
    
    response = client.get("/get_all?user_id=1")
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "count": 1,
        "memories": mock_memories
    }

@patch('main.memory')
def test_get_all_memories_error(mock_memory):
    mock_memory.get_all = MagicMock(side_effect=Exception("Get all error"))
    
    response = client.get("/get_all?user_id=1")
    
    assert response.status_code == 200
    assert response.json() == {"status": "error", "error": "Get all error"}

if __name__ == "__main__":
    pytest.main([__file__])